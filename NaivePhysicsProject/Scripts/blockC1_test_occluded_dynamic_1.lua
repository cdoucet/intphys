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


-- This module defines a test configuration for the block C1: a single
-- change and a single occluder, with moving spheres

local uetorch = require 'uetorch'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local check_occlusion = require 'check_occlusion'


local M = {}

local main_actor
local iteration

local is_visible_start = true
local is_possible = true
local is_trick_done = false


function M.initialize(_iteration, params)
   iteration = _iteration
   main_actor = spheres.get_sphere(assert(params.index))

   if iteration.type == 5 then
      for i = 1, spheres.get_max_spheres() do
         if i ~= params.index then
            uetorch.DestroyActor(spheres.get_sphere(i))
         end
      end
   else
      if iteration.type == 1 then
         is_visible_start = false
         is_possible = true
      elseif iteration.type == 2 then
         is_visible_start = true
         is_possible = true
      elseif iteration.type == 3 then
         is_visible_start = false
         is_possible = false
      elseif iteration.type == 4 then
         is_visible_start = true
         is_possible = false
      end

      uetorch.SetActorVisible(main_actor, is_visible_start)
   end
end


function M.tick(step)
   if (iteration.type ~= 5 and not is_possible
          and not is_trick_done and check_occlusion.is_middle_of_occlusion(5, step))
   then
      uetorch.SetActorVisible(main_actor, not is_visible_start)
      is_trick_done = true
   end
end


function M.get_occlusion_check_iterations()
   return {5}
end


function M.is_possible()
   return is_possible
end


function M.get_main_actor()
   return main_actor
end


function M.is_main_actor_visible()
   return (is_possible and is_visible_start) -- visible all time
      or (not is_possible and is_visible_start and not is_trick_done) -- visible 1st half
      or (not is_possible and not is_visible_start and id_trick_done) -- visible 2nd half
end


-- Return random parameters for the C1 dynamic_1 block
function M.get_random_parameters()
   local params = {}

   -- occluder
   params.occluders = {}
   params.occluders.n_occluders = 1
   params.occluders.occluder_1 = {
      material = occluders.random_material(),
      movement = 1,
      scale = {
         x = 0.5,
         y = 1,
         z = 1 - 0.5 * math.random()},
      location = {
         x = 50,
         y = -250},
      rotation = 0,
      start_position = 'down',
      pause = {math.random(5), math.random(5)}}

   -- spheres
   params.spheres = {}
   params.spheres.n_spheres = spheres.random_n_spheres()
   for i = 1, params.spheres.n_spheres do
      local p = {}

      p.material = spheres.random_material()
      p.scale = 0.9
      p.is_static = false
      p.location = {
         x = -400,
         y = -350 - 150 * (i - 1),
         z = 70 + math.random(200)}
      p.force = {
         x = math.random(8e5, 1.1e6),
         y = 0,
         z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

      if spheres.random_side() == 'right' then
         p.location.x = 500
         p.force.x = -1 * p.force.x
      end

      params.spheres['sphere_' .. i] = p
   end

   params.index = math.random(1, params.spheres.n_spheres)

   -- others
   params.floor = floor.random()
   params.light = light.random()
   params.backwall = backwall.random()

   return params
end


return M
