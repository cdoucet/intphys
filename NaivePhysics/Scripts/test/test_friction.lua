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


-- This module demonstrates the change of an actor's
-- friction/restitution coeficients at runtime

local uetorch = require 'uetorch'
local backwall = require 'backwall'
local floor = require 'floor'
local light = require 'light'
local actors = require 'actors'
local material = require 'material'
local camera = require 'camera'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'


local M = {}



function M.get_random_parameters()
   local p = { --backwall = backwall.get_random_parameters(),
      floor = 'Test/M_Ice',
      light = light.get_random_parameters()}

   p.objects = {}
   p.objects.object_1 = {
      scale = utils.location(1, 1, 1),
      mesh = 'sphere',
      material = material.random('actor'),
      location = {x = 500, y = -320, z = 70},
      rotation = {pitch = 0, roll = 0, yaw = 0},
      force = {x = -1e6, y = 0, z = 0}
   }

   p.objects.object_2 = {
      scale = utils.location(1, 1, 1),
      mesh = 'cube',
      material = material.random('actor'),
      location = {x = 500, y = -200, z = 70},
      rotation = {pitch = 0, roll = 0, yaw = 0},
      force = {x = -1e6, y = 0, z = 0}
   }

   p.objects.object_3 = {
      scale = utils.location(1, 1, 1),
      material = material.random('actor'),
      mesh = 'cylinder',
      location = {x = 500, y = -440, z = 70},
      rotation = {pitch = 0, yaw = 0, roll = 90},
      force = {x = -1e6, y = 0, z = 0}}

   -- p.actors.cone_1 = {
   --    material = material.random('actor'),
   --    scale = 1,
   --    is_static = false,
   --    location = {x = 500, y = -80, z = 70},
   --    force = {x = -0.5e6, y = 0, z = 0}}

   --print(p.floor)

   return p
end


function M.initialize()
   local floor_actor = floor.get_actor().floor
   --material.set_actor_material(floor_actor, 'M_Ice')
   material.set_physical(floor_actor, 'Ice')

   tick.add_hook(
      function()
         -- if tick.get_counter() % 10 == 0 then
         --    print('ice friction:' .. material.get_physical_properties(floor_actor).friction)
         -- end

         -- if tick.get_counter() == 25 then
         --    material.set_physical(floor_actor, 'F0R1')
         -- end

         if tick.get_counter() == 20 then
            material.set_physical(floor_actor, 'F1R0')
         end

      end, 'slow')
end


function M.get_main_object() return nil end
function M.get_occlusion_check_iterations() return {} end
function M.is_test_valid() return false end

return M
