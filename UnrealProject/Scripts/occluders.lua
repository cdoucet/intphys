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


-- This module defines the occluders behavior.
--
-- Generation of random parameters, setup of up to 2 occluders, a tick
-- method handling the occluders movements.

local uetorch = require 'uetorch'
local utils = require 'utils'
local material = require 'material'

local M = {}


-- the occluder's actors defined in the scene
local occluder_actors = {
   assert(uetorch.GetActor('Occluder_1')),
   assert(uetorch.GetActor('Occluder_2'))
}


-- Return an occluder actor
--
-- `i` must be 1 or 2 for occluder1 or occluder2 respectively
function M.get_occluder(i)
   assert(i == 1 or i == 2)
   return occluder_actors[i]
end


-- Return a random wall texture for an occluder
function M.random_material()
   return math.random(#material.wall_materials)
end


-- Select a random round trip for the occluder (0 -> no motion, 0.5 ->
-- single one way, 1 -> one round trip, 1.5 -> one round trip and one
-- more single, 2 -> 2 round trips)
function M.random_movement()
   return math.random(0, 4) / 2
end


-- Return a brief pause between each movement steps
--
-- `movement` is as returned by occluder.movement()
function M.random_pause(movement)
   local p = {}
   for i=1, movement*2 do
      table.insert(p, math.random(50))
   end
   return p
end


-- Return a random position on the X and Y axes
--
-- TODO actually nothing random here...
-- `id` must be 1 or 2 for occluder1 or occluder2 respectively
function M.random_location(id)
   local shift = 0
   if id == 2 then
      shift = 500
   end

   return {x = shift - 300, y = -150 - shift}
end


-- Return a random rotation on the Z axis in degree
function M.random_rotation()
   return math.random(-45, 45)
end


-- Return the occluder start position
--
-- Start position is randomly 'up' or 'down'
function M.random_start_position()
   return (math.random(0, 1) == 1 and 'up' or 'down')
end


-- Return a random scale for occluder dimensions
function M.random_scale()
   return {
      x = math.random() + 0.5,
      y = 1,
      z = 1.5 - 0.3 * math.random()
   }
end


-- Return a random set of parameters to setup an occluder
function M.random()
   local params = {}

   params.n_occluders = math.random(1, 2)
   for i = 1, params.n_occluders do
        local p = {
           material = M.random_material(),
           movement = M.random_movement(),
           scale = M.random_scale(),
           location = M.random_location(i),
           rotation = M.random_rotation(),
           start_position = M.random_start_position()
        }
        p.pause = M.random_pause(p.movement)

        params['occluder_' .. i] = p
   end

   return params
end


function M.insert_masks(actors, text, params)
   for i = 1, params.n_occluders do
      table.insert(actors, M.get_occluder(i))
      table.insert(text, 'occluder_' .. i)
   end
end


-- This table registers the parametrized occluders. It is built in
-- occluder.setup() and used in occluder.tick()
local occluder_register = {}


-- Initialize the occluders with given parameters.
--
-- `params` must be a table structured as the one returned by
--     occluder.random().
function M.setup(params)
   for i = 1, params.n_occluders do
      local mesh = M.get_occluder(i)
      local box = uetorch.GetActorBounds(mesh).boxY
      local p = params['occluder_' .. i]

      material.SetActorMaterial(mesh, material.wall_materials[p.material])
      uetorch.SetActorScale3D(mesh, p.scale.x, p.scale.y, p.scale.z)

      if p.start_position == 'up' then
         uetorch.SetActorRotation(mesh, 0, p.rotation, 0)
         uetorch.SetActorLocation(mesh, p.location.x, p.location.y, 20)
      else -- down
         uetorch.SetActorRotation(mesh, 0, p.rotation, 90)
         uetorch.SetActorLocation(mesh, p.location.x, p.location.y, 20 + box)
      end

      -- register the occluder for motion (through the occluder.tick
      -- method). If movement==0, the occluder remains static and do
      -- nothing on ticks.
      if p.movement > 0 then
         table.insert(
            occluder_register, {
               id=i,
               mesh=mesh,
               box=box,
               rotation=p.rotation,
               movement=p.movement,
               pause=p.pause,
               status='pause',
               t_rotation=0,
               t_rotation_change=0})
      end
   end

   for i = params.n_occluders+1, 2 do
      uetorch.DestroyActor(M.get_occluder(i))
   end

   utils.AddTickHook(M.tick)
end


local function _occluder_pause(occ)
   occ.pause[1] = occ.pause[1] - 1
   if occ.pause[1] == 0 then
      -- go to the next movement: if down, go up, if up, go down
      if uetorch.GetActorRotation(occ.mesh).roll >= 89 then
         occ.status = 'go_up'
      else
         occ.status = 'go_down'
      end
   end
end


local function _occluder_move(occ, dir, dt)
   local angle_abs = (occ.t_rotation - occ.t_rotation_change) * 20 * 0.125
   local angle_rel = angle_abs
   if dir == 1 then --go up
      angle_rel = 90 - angle_rel
   end

   local location = uetorch.GetActorLocation(occ.mesh)
   uetorch.SetActorLocation(
      occ.mesh, location.x, location.y,
      20 + math.sin((angle_rel) * math.pi / 180) * occ.box)
   uetorch.SetActorRotation(occ.mesh, 0, occ.rotation, angle_rel)

   if angle_abs >= 90 then
      table.remove(occ.pause, 1)
      occ.movement = occ.movement - 0.5
      occ.status = "pause"
      occ.t_rotation_change = occ.t_rotation
   end

   occ.t_rotation = occ.t_rotation + dt
end


function M.tick(dt)
   for n, occ in pairs(occluder_register) do
      if occ.movement > 0 then
         if occ.status == 'pause' then
            _occluder_pause(occ)
         elseif occ.status == 'go_down' then
            _occluder_move(occ, -1, dt)
         else -- 'go_up'
            _occluder_move(occ, 1, dt)
         end
      end
   end
end


return M
