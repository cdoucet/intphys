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


-- This module manages the floor actor of the scene. Setup a random
-- floor material and access to its size.

local uetorch = require 'uetorch'
local material = require 'material'


-- The floor actor defined in the scene
local actor = assert(uetorch.GetActor('Floor'))


local M = {}


-- Return a random material for the floor
function M.get_random_parameters()
   return {
      material = material.random('floor'),
      friction = 0.7,
      restitution = 0.3
   }
end


-- Insert actor and name in the masking tables
function M.get_actor()
   return {floor = actor}
end


-- Return min/max coordinates for X and Y axes
function M.get_status()
   status = {}

   local bounds = uetorch.GetActorBounds(actor)
   status.minx = bounds["x"] - bounds["boxX"]
   status.maxx = bounds["x"] + bounds["boxX"]
   status.miny = bounds["y"] - bounds["boxY"]
   status.maxy = bounds["y"] + bounds["boxY"]

   return status
end

return M
