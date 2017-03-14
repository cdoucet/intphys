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


-- false if we have encoutered an illegal overlap, true otherwise
local is_valid


-- This function is called from the MainMap level blueprint when a
-- begin overlap event is triggered by the camera trigger box. `actor`
-- is the name of the actor overlapping the camera.
function camera_overlap_detected(actor)
   print('invalid scene: overlap detected on camera')
   tick.set_ticks_remaining(0)
   is_valid = false
end


-- -- This one is called when the two occluders are so close that they
-- -- overlap (can appends in train scenes)
-- function occluders_overlap_detected()
--    if not utils.file_exists(overlap_file) then
--       torch.save(overlap_file)
--       print('overlap detected between the occluders')
--    end
-- end


-- function backwall_overlap_detected(actor)
--    if not utils.file_exists(overlap_file) then
--       torch.save(overlap_file)
--       print('overlap detected between background wall and ' .. actor)
--    end
-- end


-- This module is called from the main process.
local M = {}


-- actors is a string '1st_actor 2nd_actor game_time'
function on_actor_hit(actors)
   -- print('hit: ' .. actors, M.hit_hooks)
   local actor1 = actors:gsub(' .* .*$', '')
   local actor2 = actors:gsub('^[^ ]* ', ''):gsub(' .*$', '')
   for _, f in ipairs(M.hit_hooks) do
      f(actor1, actor2)
   end
end


M.hit_hooks = {}

-- Register a tick terminating the scene when an ocverlap on the
-- camera is detected.
function M.initialize()
   is_valid = true
end


-- Return true if an overlap on the camera has been detected in the scene
function M.is_valid()
   return is_valid
end


return M
