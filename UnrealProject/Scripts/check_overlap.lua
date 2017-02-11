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


-- This modules detects any indesirable actors overlapping during a
-- scene execution (overlap on the camera, in the background wall or
-- between occluders). Once such an overlap appends, the scene is
-- ended with a fail state (so that the naive_physics.lua script rerun
-- the scene with new parameters).


local config = require 'config'
local tick = require 'tick'
local utils = require 'utils'


-- A file created empty when an overlap is detected. It serves for
-- interprocess communication (the overlap detection function and the
-- main loop run in different processes).
local overlap_file = config.get_data_path() .. 'overlap_detected.t7'


-- This function is called from the MainMap level blueprint when a
-- begin overlap event is triggered by the camera trigger box. `actor`
-- is the name of the actor overlapping the camera.
function camera_overlap_detected(actor)
   torch.save(overlap_file)
   print('overlap detected between camera and ' .. actor)
end


-- This module is called from the main process.
local M = {}


-- Register a tick terminating the scene when an ocverlap on the
-- camera is detected.
function M.initialize()
   tick.add_hook(function()
         if utils.file_exists(overlap_file) then
            tick.set_ticks_remaining(0)
         end end, 'slow')
end


-- Return true if an overlap on the camera has been detected in the scene
--
-- TODO side effect by deleting the file, is_valid returns true only
-- once (if any)
function M.is_valid()
   local valid = true
   if utils.file_exists(overlap_file) then
      os.remove(overlap_file)
      valid = false
   end
   return valid
end


return M
