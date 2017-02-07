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


-- This module defines the training configuration for the block C1.

local backwall = require 'backwall'
local camera = require 'camera'
local floor = require 'floor'
local light = require 'light'
local occluders = require 'occluders'
local spheres = require 'spheres'

local M = {}


-- Return random parameters for the C1 block, training configuration
function M.get_random_parameters()
   return {
      backwall = backwall.random(),
      camera = camera.random(),
      floor = floor.random(),
      light = light.random(),
      occluders = occluders.random(),
      spheres = spheres.random()
   }
end


return M
