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
local material = require 'material'
local occluder = {}


-- the occluder's actors defined in the scene
local occluder1 = uetorch.GetActor('Occluder_1')
local occluder2 = uetorch.GetActor('Occluder_2')


-- Return an occluder actor
--
-- `id` must be 1 or 2 for occluder1 or occluder2 respectively
function occluder.get_occluder(id)
   assert(id == 1 or id == 2)
   if id == 1 then
      return occluder1
   else
      return occluder2
   end
end


-- Return a random wall texture for an occluder
function occluder.random_material()
   return math.random(#material.wall_materials)
end


-- Select a random round trip for the occluder (0 -> no motion, 0.5 ->
-- single one way, 1 -> one round trip, 1.5 -> one round trip and one
-- more single, 2 -> 2 round trips)
function occluder.random_movement()
   return math.random(0, 4) / 2
end


-- Return a brief pause between each movement steps
--
-- `movement` is as returned by occluder.movement()
function occluder.random_pause(movement)
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
function occluder.random_location(id)
   local shift = 0
   if id == 2 then
      shift = 500
   end

   return {x = shift - 300, y = -150 - shift}
end


-- Return a random rotation on the Z axis in degree
function occluder.random_rotation()
   return math.random(-45, 45)
end


-- Return the occluder start position
--
-- Start position is randomly 'up' or 'down'
function occluder.random_start_position()
   return (math.random(0, 1) == 1 and 'up' or 'down')
end


-- Return a random scale for occluder dimensions
function occluder.random_scale()
   return {
      x = math.random() + 0.5,
      y = 1,
      z = 1.5 - 0.3 * math.random()
   }
end


-- Return a random set of parameters to setup an occluder
function occluder.random(id)
   local params = {
      material = occluder.random_material(),
      movement = occluder.random_movement(),
      scale = occluder.random_scale(),
      location = occluder.random_location(id),
      rotation = occluder.random_rotation(),
      start_position = occluder.random_start_position()
   }
   params.pause = occluder.random_pause(params.movement)

   return params
end


-- Remove an occluder from the scene
--
-- `id` must be 1 or 2 for occluder1 or occluder2 respectively
function occluder.destroy(id)
   uetorch.DestroyActor(occluder.get_occluder(id))
end


-- This table registers the parametrized occluders. It is built in
-- occluder.setup() and used in occluder.tick()
local occluder_register = {}


-- Initialize an occluder with its parameters.
--
-- `id` must be 1 or 2 for occluder1 or occluder2 respectively
-- `params` must be a table structured as the one returned by
--     occluder.random().
function occluder.setup(id, params)
   local mesh = occluder.get_occluder(id)
   local box = uetorch.GetActorBounds(mesh).boxY

   material.SetActorMaterial(mesh, material.wall_materials[params.material])
   uetorch.SetActorScale3D(mesh, params.scale.x, params.scale.y, params.scale.z)

   if params.start_position == 'up' then
      uetorch.SetActorRotation(mesh, 0, params.rotation, 0)
      uetorch.SetActorLocation(mesh, params.location.x, params.location.y, 20)
   else -- down
      uetorch.SetActorRotation(mesh, 0, params.rotation, 90)
      uetorch.SetActorLocation(mesh, params.location.x, params.location.y, 20 + box)
   end

   -- register the occluder for motion (through the occluder.tick
   -- method). If movement==0, the occluder remains static and do
   -- nothing on ticks.
   if params.movement > 0 then
      table.insert(
         occluder_register, {
            id=id,
            mesh=mesh,
            box=box,
            rotation=params.rotation,
            movement=params.movement,
            pause=params.pause,
            status='pause',
            t_rotation=0,
            t_rotation_change=0})
   end
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


function occluder.tick(dt)
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


return occluder
