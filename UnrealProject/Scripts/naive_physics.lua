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

local scene = require 'scene'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'
local backwall = require 'backwall'
local camera = require 'camera'


-- setup the screen resolution to the one defined in config
function set_resolution(dt)
   local r = config.get_resolution()
   uetorch.SetResolution(r.x, r.y)
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
local max_depth = 0

-- Save screenshot, object masks and depth field into png images
local function save_screen(step)
   local step_str = utils.pad_zeros(step, #tostring(config.get_scene_steps()))

   -- save a screen capture
   local file = iteration.path .. 'scene/scene_' .. step_str .. '.png'
   image.save(file, assert(uetorch.Screen()))

   -- active and inactive actors in the scene are required for
   -- depth and mask
   local active_actors, inactive_actors, active_names = scene.get_masks()

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
      i3:apply(function(x) return x / scene.get_nactors() end)
      image.save(mask_file, i3)
   end
end


local status_data = {}
local status = {
   push_data = function()
      local aux = {}
      for k, v in pairs(scene.get_actors()) do
         aux[k] = utils.coordinates_to_string(v)
      end

      table.insert(status_data, aux)
   end,

   save_data = function()
      local s = scene.get_status()
      s["block"] = iteration.block
      s['steps'] = status_data

      -- write the status.json with ordered keys
      local keyorder = {
         'block', 'possible', 'floor', 'camera', 'lights', 'masks_grayscale', 'steps'}
      utils.write_json(s, iteration.path .. 'status.json', keyorder)
   end
}


local step, t_tick, t_last_tick = 0, 0, 0
local function run_tick_hooks(dt)
   if t_tick - t_last_tick >= config.get_capture_interval() then
      step = step + 1

      scene.hook(step)

      if not dry_run and not config.is_check_occlusion(iteration) then
         status.push_data()
         save_screen(step)
      end

      t_last_tick = t_tick
   end
   t_tick = t_tick + dt
end


local function run_end_tick_hooks()
   if not dry_run and not config.is_check_occlusion(iteration) then
      status.save_data()
   end

   return config.update_iterations_counter(scene.end_hook())
end


function SetCurrentIteration()
   iteration = config.get_current_iteration()

   local description = 'running ' .. config.get_description(iteration)
   print(description)

   -- create subdirectories for this iteration
   paths.mkdir(iteration.path)
   if not dry_run and not config.is_visibility_check(iteration) then
         paths.mkdir(iteration.path .. 'mask')
         paths.mkdir(iteration.path .. 'scene')
         paths.mkdir(iteration.path .. 'depth')
   end

   -- prepare the scene from the current iteration
   scene.initialize(iteration)
   tick.set_ticks_remaining(config.get_scene_ticks())
   tick.add_tick_hook(run_tick_hooks)
   tick.add_end_tick_hook(run_end_tick_hooks)

   -- tweak to force the required resolution
   tick.add_tick_hook(set_resolution)

   -- RunBlock will be called from blueprint after this function
   -- returns
   RunBlock = function() return scene.run() end
end
