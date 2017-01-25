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


-- This module manages the lighting of the scene

local uetorch = require 'uetorch'
local light = {}

-- local sky_sphere = uetorch.GetActor('SkySphere')
local directional_light = uetorch.GetActor('LightSource')


function light.random_rotation()
   return {
      x = -90 * math.random(), -- in [-90, 0]
      y = 190 + 160 * math.random(), -- in [190, 350]
      z = 360 * math.random()
   }
end

function light.random()
   return {rotation = light.random_rotation()}
end


function light.setup(params)
   local r = params.rotation
   -- print('light is ' .. math.floor(r.x) .. ' ' .. math.floor(r.y) .. ' ' .. math.floor(r.z))
   uetorch.SetActorRotation(directional_light, r.x, r.y, r.z)
end

return light
