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


-- functions called from Unreal Engine blueprints
GetCurrentIteration = config.get_current_index
RunBlock = nil

-- replace uetorch's Tick function and set a constant tick rate at 8
-- Hz (in the game timescale)
Tick = tick.tick
tick.set_tick_delta(1/8)


local iteration = nil
local screen_table, depth_table = {}, {}
local t_last_save_screen = 0
local t_save_screen = 0
local step = 0
local max_depth = 0


-- Save screenshot, object masks and depth field into png images
local function save_screen(dt)
   if t_save_screen - t_last_save_screen >= config.get_capture_interval() then
      step = step + 1
      local step_str = utils.pad_zeros(step, 3)

      -- save the screen
      local file = iteration.path .. 'scene/scene_' .. step_str .. '.png'
      local i1 = uetorch.Screen()
      if i1 then
         image.save(file, i1)
      end

      -- active and inactive actors in the scene are required for
      -- depth and mask
      local active_actors, inactive_actors, active_names = block.get_masks()

      -- compute the depth field and objects segmentation masks
      local depth_file = iteration.path .. 'depth/depth_' .. step_str .. '.png'
      local mask_file = iteration.path .. 'mask/mask_' .. step_str .. '.png'
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
         i3:apply(function(x) return x / block.nactors() end)
         image.save(mask_file, i3)
      end

      t_last_save_screen = t_save_screen
   end
   t_save_screen = t_save_screen + dt
end


local data = {}
local t_save_text = 0
local t_last_save_text = 0

local function save_status_to_table(dt)
   local aux = {}
   if t_save_text - t_last_save_text >= config.get_capture_interval() then
      for k, v in pairs(block.actors) do
         aux[k] = utils.coordinates_to_string(v)
      end
      table.insert(data, aux)

      t_last_save_text = t_save_text
   end
   t_save_text = t_save_text + dt
end


local visibility_table = {}
local t_check, t_last_check = 0, 0
local step_visibility = 0
local hidden = false
local is_hidden = {}

local function check_visibility(dt)
   if t_check - t_last_check >= config.get_capture_interval() then
      step = step + 1
      local stepStr = utils.pad_zeros(step, 3)

      local i2 = uetorch.ObjectSegmentation({block.main_actor()})
      if i2 then
         if torch.max(i2) == 0 then
            hidden = true
         else
            hidden = false
         end
      end

      table.insert(is_hidden, hidden)
      t_last_check = t_check
   end
   t_check = t_check + dt
end


local function save_data()
   if config.is_visibility_check(iteration) then
      local n_hidden = #is_hidden

      for k = 1, n_hidden do
         if not is_hidden[k] then
            break
         else
            is_hidden[k] = false
         end
      end

      for k = n_hidden, 1, -1 do
         if not is_hidden[k] then
            break
         else
            is_hidden[k] = false
         end
      end

      torch.save(iteration.path .. '../hidden_' .. iteration.type .. '.t7', is_hidden)
   else
      local status = block.get_status()
      status["block"] = iteration.block
      status['steps'] = data

      -- write the status.json with ordered keys
      local keyorder = {
         'block', 'possible', 'floor', 'camera', 'lights', 'masks_grayscale', 'steps'}
      utils.write_json(status, iteration.path .. 'status.json', keyorder)
   end
end


function SetCurrentIteration()
   iteration = config.get_current_iteration()

   local description = 'running ' .. config.get_description(iteration)
   print(description)

   -- create subdirectories for this iteration
   paths.mkdir(iteration.path)
   if not dry_run then
      paths.mkdir(iteration.path .. 'mask')
      if not config.is_visibility_check(iteration) then
         paths.mkdir(iteration.path .. 'scene')
         paths.mkdir(iteration.path .. 'depth')
      end
   end

   -- prepare the block for either train or test
   block = require(iteration.block)
   block.set_block(iteration)

   -- RunBlock will be called from blueprint
   RunBlock = function() return block.run_block() end

   tick.set_ticks_remaining(config.get_scene_ticks())

   -- BUGFIX tweak to force the first iteration to be at the required
   -- resolution
   tick.add_tick_hook(set_resolution)

   if config.is_visibility_check(iteration) then
      tick.add_tick_hook(check_visibility)
      tick.add_tick_hook(save_status_to_table)
      tick.add_end_tick_hook(save_data)
   else
      -- save screen, depth and mask
      if not dry_run then
         tick.add_tick_hook(save_screen)
         tick.add_tick_hook(save_status_to_table)
         tick.add_end_tick_hook(save_data)
      end
   end

   if iteration.type == -1 then  -- train
      tick.add_end_tick_hook(
         function(dt) return config.update_iterations_counter(true) end)
   else  -- test
      tick.add_tick_hook(block.save_check_info)
      tick.add_end_tick_hook(block.check)
   end
end
