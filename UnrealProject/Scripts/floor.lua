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
local M = {}


-- The floor actor defined in the scene
M.actor = assert(uetorch.GetActor('Floor'))


-- Return a random material for the floor
function M.random()
   return math.random(#material.ground_materials)
end


-- Insert actor and name in the masking tables
function M.insert_masks(actors, text)
   table.insert(actors, M.actor)
   table.insert(text, "floor")
end


-- Setup the floor with a random material
function M.setup(floor_material)
   floor_material = floor_material or M.random()
   material.SetActorMaterial(M.actor, material.ground_materials[floor_material])
end


-- Return min/max coordinates for X and Y axes
function M.get_status()
   status = {}

   local bounds = uetorch.GetActorBounds(M.actor)
   status.minx = bounds["x"] - bounds["boxX"]
   status.maxx = bounds["x"] + bounds["boxX"]
   status.miny = bounds["y"] - bounds["boxY"]
   status.maxy = bounds["y"] + bounds["boxY"]

   return status
end

return M
