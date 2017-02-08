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

local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'
local check_coordinates = require 'check_coordinates'

local M = {}

local main_actor
local is_visible_start
local trick1, trick2 = false, false
local trick_start, trick_stop
local xdiff_start, xdiff_stop


-- Return +1 if x if at the left of the main actor, -1 at the right
local function xdiff(x)
   return utils.sign(uetorch.GetActorLocation(main_actor).x - x)
end


function M.initialize(iteration, params)
   main_actor = spheres.get_sphere(assert(params.index))
   trick_start = assert(params.trick_start)
   trick_stop = assert(params.trick_stop)

   check_coordinates.initialize(iteration, main_actor)

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

   -- no occluder for a visible test
   occluders.remove_all()
   uetorch.SetActorVisible(main_actor, is_visible_start)
end


function M.tick(step)
   if not xdiff_start then
      xdiff_start = xdiff(trick_start)
      xdiff_stop = xdiff(trick_stop)
   end

   check_coordinates.tick()

   if not is_possible then
      if not trick1 and xdiff(trick_start) ~= xdiff_start then
         trick1 = true
         uetorch.SetActorVisible(main_actor, not is_visible_start)
      end

      if trick1 and not trick2 and xdiff(trick_stop) ~= xdiff_stop then
         trick2 = true
         uetorch.SetActorVisible(main_actor, is_visible_start)
      end
   end
end


function M.final_tick()
   return check_coordinates.final_tick()
end


function M.is_possible()
   return is_possible
end


function M.get_main_actor()
   return main_actor
end


function M.is_main_actor_visible()
   return (possible and is_visible_start) -- visible all time
      or (not possible and is_visible_start and not trick1 and not trick2) -- visible 1st third
      or (not possible and not is_visible_start and trick1 and not trick2) -- visible 2nd third
      or (not possible and is_visible_start and trick1 and trick2) -- visible 3rd third
end


-- Return random parameters for the C1 dynamic_1 block
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
      p.location = {
         x = -400,
         y = -350 - 150 * (i - 1),
         z = 70 + math.random(200)}
      p.force = {
         x = math.random(8e5, 1.1e6),
         y = 0,
         z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

      p.side = spheres.random_side()
      if p.side == 'right' then
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

   -- length and start position (on the x axis) of the magic
   -- disparition/apparition of a sphere
   local trick_length = math.random() * 250 + 200
   local main_actor_side = assert(params.spheres['sphere_' .. params.index].side)
   if main_actor_side == 'right' then
      params.trick_start = math.random() * (400 - trick_length) + trick_length
      params.trick_stop = params.trick_start - trick_length
   else
      params.trick_start = math.random() * (400 - trick_length)
      params.trick_stop = params.trick_start + trick_length
   end

   return params
end


return M
