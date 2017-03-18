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


-- This module manages the lighting of the scene, the number of active
-- lights and the presence/absence of clouds. It depends on the floor
-- module to pick a random location for the lights in the ground
-- boundaries.
--
-- TODO would be better to spawn the lights at runtime
-- TODO control parameters of the sky sphere from here

local uetorch = require 'uetorch'
local utils = require 'utils'
local floor = require 'floor'


local nlights

local M = {}


-- local sky_sphere = assert(uetorch.GetActor('Sky_Sphere'))
local directional_lights = {
   assert(uetorch.GetActor('LightSource1')),
   assert(uetorch.GetActor('LightSource2'))
}


-- Return random parameters for the scene illumination
--
-- Choose 1 or 2 directional light with random orientation, and the
-- presence/absence of the sky sphere (with clouds)
function M.get_random_parameters()
   local params = {}

   nlights = math.random(1, 2)
   for i = 1, nlights do
      local b = floor.get_status()
      params['light_' .. i] = {
         location = utils.location(
            math.random() * (b.maxx - b.minx) + b.minx,
            math.random() * (b.maxy - b.miny) + b.miny,
            math.random() * 200 + 100),
         rotation = utils.rotation(
            math.random() * 80 - 90, math.random() * 360, 0)
      }
   end

   params.is_sky = (math.random() >= 0.5)

   return params
end


-- Lights are directional, so only the rotation vector is reported in
-- the status (location doesn't matter)
function M.get_status()
   local status = {}
   for i = 1, nlights do
      status['light_' .. i] = utils.coordinates_to_string(directional_lights[i])
   end
   return status
end


return M
