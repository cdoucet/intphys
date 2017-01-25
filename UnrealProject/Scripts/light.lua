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
local light = {}

local sky_sphere = uetorch.GetActor('SkySphere')
local directional_lights = {
   uetorch.GetActor('LightSource'),
   uetorch.GetActor('LightSource2')
}


-- Return a random rotation vector for a directional light orientation
function light.random_directional()
   return {
      x = -90 * math.random(),
      y = 190 + 160 * math.random(), -- in [190, 350]
      z = 360 * math.random()
   }
end


-- Return a random rotation vector for the sky sphere
function light.random_sky()
   return {
      x = 360 * math.random(),
      y = 360 * math.random(),
      z = 360 * math.random()
   }
end


-- Return random parameters for the scene illumination
--
-- Choose 1 or 2 directional light with random orientation, and the
-- presence/absence of the sky sphere (with clouds)
function light.random()
   local params = {}

   params.nlights = (math.random() >= 0.5 and 2 or 1)
   params.directional = {}
   for i = 1, params.nlights do
      table.insert(params.directional, light.random_directional())
   end

   params.is_sky = (math.random() >= 0.5)
   if params.is_sky then
      params.sky = light.random_sky()
   end

   return params
end


--- Setup the scene illumination with the given parameters
function light.setup(params)
   -- setup the lights
   for i = 1, params.nlights do
      local d = params.directional[i]
      uetorch.SetActorRotation(directional_lights[i], d.x, d.y, d.z)
   end

   -- desactivate any unused light
   for i = params.nlights + 1, #directional_lights do
      uetorch.DestroyActor(directional_lights[i])
   end

   -- setup the sky sphere
   if params.is_sky then
      local s = params.sky
      uetorch.SetActorRotation(sky_sphere, s.x, s.y, s.z)
   else
      uetorch.DestroyActor(sky_sphere)
   end
end

return light
