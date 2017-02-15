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
-- change and a single occluder, with static spheres.

local uetorch = require 'uetorch'
local config = require 'config'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local check_occlusion = require 'check_occlusion'


local M = {}

local main_actor
local data_occlusion
local iteration
local is_visible_start
local is_possible
local is_trick_done


function M.initialize(_iteration, params)
   iteration = _iteration
   main_actor = spheres.get_sphere(assert(params.index))
   is_trick_done = false

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
   if (iteration.type ~= 5 and not is_trick_done
          and not is_possible and check_occlusion.is_middle_of_occlusion(5, step))
   then
      is_trick_done = true
      uetorch.SetActorVisible(main_actor, not is_visible_start)
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
      or (not is_possible and not is_visible_start and is_trick_done) -- visible 2nd half
end


-- Return random parameters for the C1 block, static test
function M.get_random_parameters()
   local params = {}

   -- occluders
   params.occluders = {}
   params.occluders.n_occluders = 1
   params.occluders.occluder_1 = {
      material = occluders.random_material(),
      movement = 1,
      scale = {
         x = 1 - 0.4 * math.random(),
         y = 1,
         z = 1 - 0.5 * math.random()},
      rotation = 0,
      start_position = 'down',
      pause = {math.random(20), math.random(20)}
   }
   params.occluders.occluder_1.location = {
      x = 100 - 200 * params.occluders.occluder_1.scale.x, y = -350}

   -- spheres
   params.spheres = {}
   params.spheres.n_spheres = spheres.random_n_spheres()
   local x_loc = {150, 40, 260}
   for i = 1, params.spheres.n_spheres do
      local p = {}

      p.material = spheres.random_material()
      p.scale = 1
      p.is_static = true
      p.location = {x = x_loc[i], y = -550, z = 70}

      params.spheres['sphere_' .. i] = p
   end
   params.index = math.random(1, params.spheres.n_spheres)

   -- static actors
   params.floor = floor.random()
   params.light = light.random()
   params.backwall = backwall.random()

   return params
end


return M
