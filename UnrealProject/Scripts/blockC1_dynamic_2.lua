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

local material = require 'material'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'

local M = {}
M.actors = {}

local iteration
local params = {}

local is_hidden1, is_hidden2
local visible1 = true
local visible2 = true
local possible = true
local trick1 = false
local trick2 = false

local t_check, t_last_check = 0, 0
local step = 0

local function trick(dt)
   if t_check - t_last_check >= config.get_capture_interval(iteration) then
      step = step + 1

      if params.spheres['sphere_' .. params.index].side == 'left' then
         if not trick1 and is_hidden1[step] then
            trick1 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible2)
         end

         if trick1 and not trick2 and is_hidden2[step] then
            trick2 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible1)
         end
      else
         if not trick1 and is_hidden2[step] then
            trick1 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible2)
         end

         if trick1 and not trick2 and is_hidden1[step] then
            trick2 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible1)
         end
      end

      t_last_check = t_check
   end
   t_check = t_check + dt
end


local main_actor
function M.main_actor()
   return main_actor
end


function M.get_masks()
   local active, inactive, text = {}, {}, {}

   floor.insert_masks(active, text)
   backwall.insert_masks(active, text, params.backwall)
   occluders.insert_masks(active, text, params.occluders)

   -- on test, the main actor only can be inactive (when hidden)
   for i = 1, params.spheres.n_spheres do
      table.insert(text, 'sphere_' .. i)
      if i ~= params.index then
         table.insert(active, spheres.get_sphere(i))
      end
   end

   -- We add the main actor as active only when it's not hidden
   if (possible and visible1) -- visible all time
      or (not possible and visible1 and not trick1 and not trick2) -- visible 1st third
      or (not possible and visible2 and trick1 and not trick2) -- visible 2nd third
      or (not possible and visible1 and trick1 and trick2) -- visible 3rd third
   then
      table.insert(active, main_actor)
   else
      table.insert(inactive, main_actor)
   end

   return active, inactive, text
end


function M.get_nactors()
   local max = 3 -- floor + 2 occluders
   if params.backwall.is_active then
      max = max + 1
   end
   return max + params.spheres.n_spheres
end


-- Return random parameters for the C1 dynamic_2 block
local function get_random_parameters()
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


function M.set_block(iteration)
   if iteration.type == 6 then
      if config.get_load_params() then
         params = utils.read_json(iteration.path .. '../params.json')
      else
         params = get_random_parameters()
         utils.write_json(params, iteration.path .. '../params.json')
      end

      uetorch.DestroyActor(occluders.get_occluder(2))
   else
      params = utils.read_json(iteration.path .. '../params.json')

      if iteration.type == 5 then
         uetorch.DestroyActor(occluders.get_occluder(1))
      else
         is_hidden1 = torch.load(iteration.path .. '../hidden_6.t7')
         is_hidden2 = torch.load(iteration.path .. '../hidden_5.t7')
         tick.add_tick_hook(trick)

         if iteration.type == 1 then
            visible1 = false
            visible2 = false
            possible = true
         elseif iteration.type == 2 then
            visible1 = true
            visible2 = true
            possible = true
         elseif iteration.type == 3 then
            visible1 = false
            visible2 = true
            possible = false
         elseif iteration.type == 4 then
            visible1 = true
            visible2 = false
            possible = false
         end
      end
   end

   if iteration.type == 5 or iteration.type == 6 then
      for i = 1, params.spheres.n_spheres do
         if i ~= params.index then
            uetorch.DestroyActor(spheres.get_sphere(i))
         end
      end
   end

   main_actor = spheres.get_sphere(params.index)
   M.actors['occluder_1'] = occluders.get_occluder(1)
   M.actors['occluder_2'] = occluders.get_occluder(2)
   for i = 1,params.spheres.n_spheres do
      M.actors['sphere_' .. i] = spheres.get_sphere(i)
   end
end

function M.run_block()
   -- camera, floor, lights and background wall
   camera.setup(config.get_current_iteration(), 150)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)
   occluders.setup(params.occluders)
   spheres.setup(params.spheres)

   uetorch.SetActorVisible(main_actor, visible1)
end

local check_data = {}
local save_tick = 1

function M.save_check_info(dt)
   local aux = {}
   aux.location = uetorch.GetActorLocation(main_actor)
   aux.rotation = uetorch.GetActorRotation(main_actor)
   table.insert(check_data, aux)
   save_tick = save_tick + 1
end


function M.check()
   local iteration = config.get_current_iteration()
   local status = true

   torch.save(iteration.path .. '../check_' .. iteration.type .. '.t7', check_data)

   if iteration.type == 6 then
      local is_hidden1 = torch.load(iteration.path .. '../hidden_6.t7')
      local found_hidden = false
      for i = 1,#is_hidden1 do
         if is_hidden1[i] then
            found_hidden = true
         end
      end

      if not found_hidden then
         -- file:write("Iteration check failed on condition 1: not hidden in visibility check 1\n")
         status = false
      end
   end

   if iteration.type == 5 then
      local is_hidden2 = torch.load(iteration.path .. '../hidden_5.t7')
      local found_hidden = false
      for i = 1,#is_hidden2 do
         if is_hidden2[i] then
            found_hidden = true
         end
      end

      if not found_hidden then
         status = false
      end
   end

   if iteration.type < 6 and status then
      local ticks = config.get_scene_ticks()
      local prev_data = torch.load(iteration.path .. '../check_' .. (iteration.type + 1) .. '.t7')

      local max_diff = 1e-6
      for t = 1, ticks do
         -- check location values
         if((math.abs(check_data[t].location.x - prev_data[t].location.x) > max_diff) or
               (math.abs(check_data[t].location.y - prev_data[t].location.y) > max_diff) or
               (math.abs(check_data[t].location.z - prev_data[t].location.z) > max_diff) or
               (math.abs(check_data[t].rotation.pitch - prev_data[t].rotation.pitch) > max_diff) or
               (math.abs(check_data[t].rotation.yaw - prev_data[t].rotation.yaw) > max_diff) or
            (math.abs(check_data[t].rotation.roll - prev_data[t].rotation.roll) > max_diff)) then
            status = false
         end
      end
   end

   config.update_iterations_counter(status)
end

function M.is_possible()
   return possible
end


function M.get_status()
   local nactors = M.get_nactors()
   local _, _, actors = M.get_masks()
   actors = backwall.get_updated_actors(actors)

   local masks = {}
   masks[0] = "sky"
   for n, m in pairs(actors) do
      masks[math.floor(255 * n/ nactors)] = m
   end

   local status = {}
   status['possible'] = M.is_possible()
   status['floor'] = floor.get_status()
   status['camera'] = camera.get_status()
   status['lights'] = light.get_status()
   status['masks_grayscale'] = masks

   return status
end


return M
