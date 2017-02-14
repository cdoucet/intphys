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


-- This module is entry point of the program, it is called from the
-- packaged game. It configures the current iteration scene and run
-- it, manages the random seed and data saving (screen captures)

local uetorch = require 'uetorch'
local paths = require 'paths'
local posix = require 'posix'
local config = require 'config'
local saver = require 'saver'
local scene = require 'scene'
local tick = require 'tick'
local check_overlap = require 'check_overlap'


local M = {}


function M.initialize()
   -- setup the random seed and update it for the next iteration
   local seed = os.getenv('NAIVEPHYSICS_SEED') or os.time()
   math.randomseed(seed)
   posix.setenv('NAIVEPHYSICS_SEED', seed + 1)

   -- ticking at a constant rate
   tick.initialize(config.get_ticks_rate())
end


function M.conclude()
   local is_valid_scene = scene.final_tick() and check_overlap.is_valid()

   local remaining_iterations = config.prepare_next_iteration(is_valid_scene)
   if remaining_iterations == 0 then
      print('no more iteration, exiting')
      uetorch.ExecuteConsoleCommand('Exit')
   else
      uetorch.ExecuteConsoleCommand('RestartLevel')
   end
end


function run_current_iteration()
   -- retrieve the current iteration and display a little description
   local iteration = config.get_current_iteration()
   local description = 'running ' .. config.get_description(iteration)
   print(description)

   -- create a subdirectory for this iteration
   paths.mkdir(iteration.path)

   -- prepare the scene for the current iteration and register it for
   -- ticking. At the final tick we update the iteration counter to
   -- prepare the next iteration or, if the current iteration failed,
   -- retry it with new parameters.
   scene.initialize(iteration)
   tick.add_hook(scene.tick, 'slow')
   tick.add_hook(M.conclude, 'final')

   -- initialize the overlap check. The scene will fail if any illegal
   -- overlaping between actors is detected.
   check_overlap.initialize()

   -- initialize the saver to write status.json and screen
   -- captures. We save data only if not in dry mode or during an
   -- occlusion check.
   local dry_run = os.getenv('NAIVEPHYSICS_DRY') or config.is_check_occlusion(iteration)
   if not dry_run then
      saver.initialize(iteration, scene, config.get_nticks())
      tick.add_hook(saver.tick, 'slow')
      tick.add_hook(saver.final_tick, 'final')
   end
end


return M
