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
-- lights and the presence/absence of clouds.

local uetorch = require 'uetorch'
local utils = require 'utils'


local M = {}


local sky_sphere = assert(uetorch.GetActor('SkySphere'))
local directional_lights = {
   assert(uetorch.GetActor('LightSource_1')),
   assert(uetorch.GetActor('LightSource_2'))
}


-- Return random parameters for the scene illumination
--
-- Choose 1 or 2 directional light with random orientation, and the
-- presence/absence of the sky sphere (with clouds)
function M.get_random_parameters()
   local params = {}

   params.nlights = (math.random() >= 0.5 and 2 or 1)
   params.directional = {}
   for i = 1, params.nlights do
      -- random rotation vector for a directional light orientation
      table.insert(params.directional,
                   {x = -25 - 40 * math.random(),
                    y = 150 + 120 * math.random(),
                    z = 360 * math.random()})
   end

   params.is_sky = (math.random() >= 0.5)

   return params
end


--- Setup the scene illumination with the given parameters, store the
--- parameters locally
local _params = nil
function M.initialize(params)
   -- setup the lights
   for i = 1, params.nlights do
      local d = params.directional[i]
      uetorch.SetActorRotation(directional_lights[i], d.x, d.y, d.z)
   end

   -- -- desactivate any unused light
   -- for i = params.nlights + 1, #directional_lights do
   --    uetorch.DestroyActor(directional_lights[i])
   -- end

   -- -- setup the sky sphere
   -- if not params.is_sky then
   --    uetorch.DestroyActor(sky_sphere)
   -- end

   _params = params
end


-- Lights are directional, so only the rotation vector is reported in
-- the status (location doesn't matter)
function M.get_status()
   local status = {}
   for i = 1, _params.nlights do
      status['light_' .. i] = utils.rotation_to_string(directional_lights[i])
   end

   return status
end


return M
