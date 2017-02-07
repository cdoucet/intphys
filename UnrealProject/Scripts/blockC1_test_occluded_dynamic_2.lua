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


-- This module defines a test configuration for the block C1: two
-- changes and two occluders, with moving spheres.

local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'
local check_occlusion = require 'check_occlusion'
local check_coordinates = require 'check_coordinates'

local M = {}

local main_actor
local main_actor_side
local iteration
local params

local visible1 = true
local possible = true
local trick1 = false
local trick2 = false


function M.initialize(_iteration, params)
   iteration = _iteration
   main_actor = spheres.get_sphere(assert(params.index))
   main_actor_side = params.spheres['sphere_' .. params.index].side

   check_occlusion.initialize(iteration, main_actor, {6, 5})
   check_coordinates.initialize(iteration, main_actor)

   if iteration.type == 6 then
      uetorch.DestroyActor(occluders.get_occluder(2))
   elseif iteration.type == 5 then
      uetorch.DestroyActor(occluders.get_occluder(1))
   else
      if iteration.type == 1 then
         visible1 = false
         possible = true
      elseif iteration.type == 2 then
         visible1 = true
         possible = true
      elseif iteration.type == 3 then
         visible1 = false
         possible = false
      elseif iteration.type == 4 then
         visible1 = true
         possible = false
      end
   end

   if iteration.type == 5 or iteration.type == 6 then
      for i = 1, params.spheres.n_spheres do
         if i ~= params.index then
            uetorch.DestroyActor(spheres.get_sphere(i))
         end
      end
   end

   uetorch.SetActorVisible(main_actor, visible1)
end


function M.tick(step)
   check_coordinates.tick()
   check_occlusion.tick()

   if iteration.type ~= 5 and iteration.type ~= 6 and not possible then
      if main_actor_side == 'left' then
         if not trick1 and check_occlusion.is_middle_of_occlusion(6, step) then
            trick1 = true
            uetorch.SetActorVisible(main_actor, not visible1)
         end

         if trick1 and not trick2 and check_occlusion.is_middle_of_occlusion(5, step) then
            trick2 = true
            uetorch.SetActorVisible(main_actor, visible1)
         end
      else
         if not trick1 and check_occlusion.is_middle_of_occlusion(5, step) then
            trick1 = true
            uetorch.SetActorVisible(main_actor, not visible1)
         end

         if trick1 and not trick2 and check_occlusion.is_middle_of_occlusion(6, step) then
            trick2 = true
            uetorch.SetActorVisible(main_actor, visible1)
         end
      end
   end
end


function M.final_tick()
   return check_occlusion.final_tick() and check_coordinates.final_tick()
end

function M.is_possible()
   return possible
end


function M.get_main_actor()
   return main_actor
end


function M.is_main_actor_visible()
   return (possible and visible1) -- visible all time
      or (not possible and visible1 and not trick1 and not trick2) -- visible 1st third
      or (not possible and not visible1 and trick1 and not trick2) -- visible 2nd third
      or (not possible and visible1 and trick1 and trick2) -- visible 3rd third
end


-- Return random parameters for the C1 dynamic_2 block
function M.get_random_parameters()
   local params = {}

   -- spheres
   params.spheres = {}
   params.spheres.n_spheres = spheres.random_n_spheres()
   for i = 1, params.spheres.n_spheres do
      local p = {}

      p.material = spheres.random_material()
      p.scale = 0.9
      p.is_static = false
      p.side = spheres.random_side()
      p.location = {
         x = -400,
         y = -550 - 150 * (i - 1),
         z = 70 + math.random(200)}
      p.force = {
         x = 1.6e6,
         y = 0,
         z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

      if p.side == 'right' then
         p.location.x = 700
         p.force.x = -1 * p.force.x
      end

      params.spheres['sphere_' .. i] = p
   end
   params.index = math.random(1, params.spheres.n_spheres)

   -- occluders
   params.occluders = {}
   params.occluders.n_occluders = 2
   params.occluders.occluder_1 = {
      material = occluders.random_material(),
      movement = 1,
      scale = {x = 0.5, y = 1, z = 1 - 0.4 * math.random()},
      location = {x = -100, y = -350},
      rotation = 0,
      start_position = 'down',
      pause = {math.random(5), math.random(5)}}

   params.occluders.occluder_2 = {
      material = occluders.random_material(),
      movement = 1,
      scale = params.occluders.occluder_1.scale,
      location = {x = 200, y = -350},
      rotation = 0,
      start_position = 'down',
      pause = {table.unpack(params.occluders.occluder_1.pause)}}

   -- others
   params.floor = floor.random()
   params.light = light.random()
   params.backwall = backwall.random()

   return params
end


return M
