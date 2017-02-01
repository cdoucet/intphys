-- Copyright 2016, 2017 Mario Ynocente Castro, Mathieu Bernard
--
-- You can redistribute this file and/or modify it under the terms of
-- the GNU General Public License as published by the Free Software
-- Foundation, either version 3 of the License, or (at your option) any
-- later version.
--
-- This program is distributed in the hope that it will be useful, but
-- WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
-- General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program. If not, see <http://www.gnu.org/licenses/>.


-- This module is entry point of the program from the Unreal Engine
-- blueprints. It configures the current iteration block and run it,
-- manages the random seed, takes sceen captures and metadata (masking
-- and depth).

local uetorch = require 'uetorch'
local paths = require 'paths'
local image = require 'image'
local posix = require 'posix'

local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'
local backwall = require 'backwall'
local camera = require 'camera'


local block


-- Force the rendered image to be 288x288
function set_resolution(dt)
   uetorch.SetResolution(288, 288)
end


-- setup the random seed
local seed = os.getenv('NAIVEPHYSICS_SEED') or os.time()
math.randomseed(seed)
posix.setenv('NAIVEPHYSICS_SEED', seed + 1)

-- Setup the dry mode: if active, do not capture any screenshot
local dry_run = os.getenv('NAIVEPHYSICS_DRY') or false

-- functions called from MainMap_CameraActor_Blueprint
GetCurrentIteration = utils.GetCurrentIteration
RunBlock = nil

-- replace uetorch's Tick function and set the tick rate at 8 Hz
Tick = tick.tick
tick.set_tick_delta(1/8)



local iterationId, iterationType, iterationBlock, iterationPath
local screenTable, depthTable = {}, {}
local tLastSaveScreen = 0
local tSaveScreen = 0
local step = 0
local max_depth = 0


-- Save screenshot, object masks and depth field into png images
local function SaveScreen(dt)
   if tSaveScreen - tLastSaveScreen >= config.GetBlockCaptureInterval(iterationBlock) then
      step = step + 1
      local stepStr = PadZeros(step, 3)

      -- save the screen
      local file = iterationPath .. 'scene/scene_' .. stepStr .. '.png'
      local i1 = uetorch.Screen()
      if i1 then
         image.save(file, i1)
      end

      -- active and inactive actors in the scene are required for
      -- depth and mask
      local active_actors, inactive_actors, active_names = block.MaskingActors()

      -- compute the depth field and objects segmentation masks
      local depth_file = iterationPath .. 'depth/depth_' .. stepStr .. '.png'
      local mask_file = iterationPath .. 'mask/mask_' .. stepStr .. '.png'
      local i2, i3 = uetorch.CaptureDepthAndMasks(
         camera.actor, active_actors, inactive_actors)

      -- save the depth field
      if i2 then
         -- normalize the depth field in [0, 1]. TODO max depth is
         -- assumed to be visible at the first tick. If this is not
         -- the case, the following normalization isn't correct as the
         -- max_depth varies accross ticks.
         max_depth = math.max(i2:max(), max_depth)
         i2:apply(function(x) return x / max_depth end)
         image.save(depth_file, i2)
      end

      -- save the objects segmentation masks
      if i3 then
         -- cluster the backwall componants in a single mask. This
         -- modifies i3 in place.
         backwall.group_masks(i3, active_actors, active_names)

         i3 = i3:float()  -- cast from int to float for normalization
         i3:apply(function(x) return x / block.MaxActors() end)
         image.save(mask_file, i3)
      end

      tLastSaveScreen = tSaveScreen
   end
   tSaveScreen = tSaveScreen + dt
end


local data = {}
local tSaveText = 0
local tLastSaveText = 0

local function SaveStatusToTable(dt)
   local aux = {}
   if tSaveText - tLastSaveText >= config.GetBlockCaptureInterval(iterationBlock) then
      for k, v in pairs(block.actors) do
         aux[k] = coordinates_to_string(v)
      end
      table.insert(data, aux)

      tLastSaveText = tSaveText
   end
   tSaveText = tSaveText + dt
end


local visibilityTable = {}
local tCheck, tLastCheck = 0, 0
local step = 0
local hidden = false
local isHidden = {}

local function CheckVisibility(dt)
   if tCheck - tLastCheck >= config.GetBlockCaptureInterval(iterationBlock) then
      step = step + 1
      local stepStr = PadZeros(step, 3)

      local actors = {block.MainActor()}
      local i2 = uetorch.ObjectSegmentation(actors)

      if i2 then
         if torch.max(i2) == 0 then
            hidden = true
         else
            hidden = false
         end
      end

      table.insert(isHidden, hidden)
      tLastCheck = tCheck
   end
   tCheck = tCheck + dt
end

local function SaveData()
   if config.IsVisibilityCheck(iterationBlock, iterationType) then
      local nHidden = #isHidden

      for k = 1,nHidden do
         if not isHidden[k] then
            break
         else
            isHidden[k] = false
         end
      end

      for k = nHidden,1,-1 do
         if not isHidden[k] then
            break
         else
            isHidden[k] = false
         end
      end

      torch.save(iterationPath .. '../hidden_' .. iterationType .. '.t7', isHidden)
   else
      local status = block.get_status()
      status["block"] = iterationBlock
      status['steps'] = data

      -- write the status.json with ordered keys
      local keyorder = {
         'block', 'possible', 'floor', 'camera', 'lights', 'masks_grayscale', 'steps'}
      WriteJson(status, iterationPath .. 'status.json', keyorder)
   end
end


function SetCurrentIteration()
   local currentIteration = utils.GetCurrentIteration()
   iterationId, iterationType, iterationBlock, iterationPath =
      config.GetIterationInfo(currentIteration)

   local descr = 'running ' .. config.IterationDescription(iterationBlock, iterationId, iterationType)
   print(descr)

   -- create subdirectories for this iteration
   paths.mkdir(iterationPath)
   if not dry_run then
      paths.mkdir(iterationPath .. 'mask')
      if not config.IsVisibilityCheck(iterationBlock, iterationType) then
         paths.mkdir(iterationPath .. 'scene')
         paths.mkdir(iterationPath .. 'depth')
      end
   end

   -- prepare the block for either train or test
   block = require(iterationBlock)
   block.SetBlock(currentIteration)

   -- RunBlock will be called from blueprint
   RunBlock = function() return block.RunBlock() end

   tick.set_ticks_remaining(config.GetBlockTicks(iterationBlock))

   -- BUGFIX tweak to force the first iteration to be at the required
   -- resolution
   tick.add_tick_hook(set_resolution)

   if config.IsVisibilityCheck(iterationBlock, iterationType) then
      tick.add_tick_hook(CheckVisibility)
      tick.add_tick_hook(SaveStatusToTable)
      tick.add_end_tick_hook(SaveData)
   else
      -- save screen, depth and mask
      if not dry_run then
         tick.add_tick_hook(SaveScreen)
         tick.add_tick_hook(SaveStatusToTable)
         tick.add_end_tick_hook(SaveData)
      end
   end

   if iterationType == -1 then  -- train
      tick.add_end_tick_hook(
         function(dt) return utils.UpdateIterationsCounter(true) end)
   else  -- test
      tick.add_tick_hook(block.SaveCheckInfo)
      tick.add_end_tick_hook(block.Check)
   end
end
