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


-- This module defines random camera position, and a function to setup
-- the camera in a given position and orientation.
--
-- TODO for now we only pick random camera coordinates for the train
-- pathway, test pathway has constant camera point of view.

local uetorch = require 'uetorch'
local utils = require 'utils'

local M = {}


-- The camera actor defined in the scene
local actor = assert(uetorch.GetActor("Camera"))


-- Return the camera actor
function M.get_actor()
   return actor
end


-- Return a random location for the camera
function M.random_location()
   return {
      math.random(-100, 100), -- x axis is left/right
      math.random(200, 400), -- y axis is front/back
      math.random(-10, 100)  -- z axis is up/down
   }
end


-- Return a radom rotation for the camera
function M.random_rotation()
   return {
      math.random(-15, 10),
      math.random(-30, 30),
      0
   }
end


-- Return random parameters for the camera
function M.random()
   return {
      location = M.random_location(),
      rotation = M.random_rotation()
   }
end


-- Setup the camera location and rotation
--
-- params must be a table structured as the one returned by
-- camera.random(). Params are considered only for train (when
-- iteration.type is -1), the camera location on the x axis varies
-- across blocks and is therefore given as a parameter.
function M.setup(iteration, x_location, params)
   if iteration.type == -1 then  -- train
      uetorch.SetActorLocation(
         M.get_actor(),
         x_location + params.location[1],
         30 + params.location[2],
         80 + params.location[3])

      uetorch.SetActorRotation(
         M.get_actor(),
         0 + params.rotation[1],
         -90 + params.rotation[2],
         0 + params.rotation[3])
   else
      uetorch.SetActorLocation(M.get_actor(), x_location, 30, 80)
      uetorch.SetActorRotation(M.get_actor(), 0, -90, 0)
   end
end


-- Return the camera location, rotation and horizontal field of view (in degree)
function M.get_status()
   return utils.coordinates_to_string(M.get_actor())
end

return M
