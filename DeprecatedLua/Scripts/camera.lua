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


-- This module manages the scene's camera. It defines and controls
-- it's location and rotation. The other camera parameters are
-- constant and fixed in the Uneral editor: a perspective projection,
-- a fixed ratio heigth/width at 1 and an horizontal field of view of
-- 90 degrees.


local uetorch = require 'uetorch'
local utils = require 'utils'


local M = {}


-- The camera actor defined in the scene, initialized during the first
-- call to the get_actor() function
local camera_actor


-- Return the camera actor defined in the scene and it's trigger box
function M.get_actor()
   if not camera_actor then
      camera_actor = assert(uetorch.GetActor('Camera_Blueprint_C_0'))
   end
   return camera_actor
end


-- Return random location and rotation parameters for the camera
function M.get_random_parameters()
   return {
      location = {
         x = 150 + math.random(-100, 100),
         y = 30 + math.random(200, 400),
         z = 80 + math.random(-10, 100)},

      rotation = {
         pitch = math.random(-15, 10),
         yaw = -90 + math.random(-30, 30),
         roll = 0}}
end


-- Return default parameters for the camera (configuration used for
-- test scenes)
function M.get_default_parameters()
   return {
      location = {x = 150, y = -100 * math.random(), z = 150 + math.random()},
      rotation = {pitch = -10 * math.random() - 5, yaw = -90, roll = 0}}
end


-- Return the camera location and rotation as a string
function M.get_status()
   return utils.coordinates_to_string(M.get_actor())
end


return M
