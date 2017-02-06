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
local posix = require 'posix'

local saver = require 'saver'
local scene = require 'scene'
local config = require 'config'
local tick = require 'tick'


-- setup the screen resolution to the one defined in config
function set_resolution(dt)
   local r = config.get_resolution()
   uetorch.SetResolution(r.x, r.y)
end


-- setup the random seed
local seed = os.getenv('NAIVEPHYSICS_SEED') or os.time()
math.randomseed(seed)
posix.setenv('NAIVEPHYSICS_SEED', seed + 1)


-- functions called from Unreal Engine blueprints
GetCurrentIteration = config.get_current_index
RunBlock = nil

-- replace uetorch's Tick function and set a constant tick rate
Tick = tick.tick
tick.set_tick_delta(1/8)


function SetCurrentIteration()
   -- retrieve the current iteration and display a little description
   local iteration = config.get_current_iteration()
   local description = 'running ' .. config.get_description(iteration)
   print(description)

   -- create a subdirectory for this iteration
   paths.mkdir(iteration.path)

   -- tweak to force the required resolution
   tick.add_hook(set_resolution, 'fast')

   -- prepare the scene for the current iteration (generating or
   -- reading params.json)
   scene.initialize(iteration)
   tick.add_hook(scene.hook, 'slow')
   tick.add_hook(
      function() return config.update_iterations_counter(scene.end_hook()) end,
      'final')

   -- setup the dry mode: if active, do not save any data except the params.json
   local dry_run = os.getenv('NAIVEPHYSICS_DRY') or config.is_check_occlusion(iteration)

   -- initialize the saver to write status.json and screen captures
   if not dry_run then
      saver.initialize(iteration, scene)
      tick.add_hook(saver.hook, 'slow')
      tick.add_hook(saver.final_hook, 'final')
   end

   -- RunBlock will be called from blueprint after this function
   -- returns
   RunBlock = scene.setup
end
