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
local tick = require 'tick'


-- the occluder's actors defined in the scene
local occluder_actors = {
   assert(uetorch.GetActor('Occluder_1')),
   assert(uetorch.GetActor('Occluder_2'))
}


-- This table registers the mobile (rotating) occluders. It is built in
-- occluder.initialize() and used in occluder.tick()
local mobile_occluders

-- Registers the active occluders, mobile or not, and their number
local active_occluders, noccluders


-- Return true if the actor is currently active in the scene
local function is_active_occluder(actor)
   for _, a in pairs(active_occluders) do
      if a == actor then
         return true
      end
   end
   return false
end


-- Internal function handling occluder's rotation
local function _occluder_move(o, dir, dt)
   local angle_abs = (o.t_rotation - o.t_rotation_change) * 20 * 0.125
   local angle_rel = angle_abs
   if dir == 1 then --go up
      angle_rel = 90 - angle_rel
   end

   local location = uetorch.GetActorLocation(o.mesh)
   uetorch.SetActorLocation(
      o.mesh, location.x, location.y,
      20 + math.sin((angle_rel) * math.pi / 180) * o.box)
   uetorch.SetActorRotation(o.mesh, 0, o.rotation, angle_rel)

   if angle_abs >= 90 then
      table.remove(o.pause, 1)
      o.movement = o.movement - 0.5
      o.status = "pause"
      o.t_rotation_change = o.t_rotation
   end

   o.t_rotation = o.t_rotation + dt
end


-- Internal function handling pause steps between occluder's rotations
local function _occluder_pause(o)
   o.pause[1] = o.pause[1] - 1
   if o.pause[1] <= 0 then
      -- go to the next movement: if down, go up, if up, go down
      if uetorch.GetActorRotation(o.mesh).roll >= 89.5 then
         o.status = 'go_up'
      else
         o.status = 'go_down'
      end
   end
end



local M = {}


function M.get_random_parameters(noccluders, subblock)
   noccluders = noccluders or math.random(1, 2)
   subblock = subblock or 'train'

   local params = {}
   for i = 1, noccluders do
      local name = 'occluder_' .. tostring(i)
      assert(i <= #occluder_actors)
      params[name] = M.get_random_occluder_parameters(name, subblock)
   end

   return params
end


-- Initialize the occluders with given parameters.
--
-- Setup the location, scale, movement and material of
-- parametrized occluders, destroy the unused ones.
--
-- `params` is a table of (occluder_name -> occluder_params), for
--     exemple as returned by the get_random_parameters() method. Each
--     occluder name must be valid and the params must have the
--     following structure:
--         {material, movement, scale, location={x, y, z},
--          rotation, start_position, pause}
--
-- `bounds` is an optional table of scene boundaries structured as
--     {xmin, xmax, ymin, ymax}. When used, the occluders location is
--     forced to be in thoses bounds.
function M.initialize(params, bounds)
   active_occluders = {}
   mobile_occluders = {}
   noccluders = 0

   for occluder_name, occluder_params in pairs(params or {}) do
      local o = M.get_occluder(occluder_name)
      local p = occluder_params

      -- the y bound box is used for occluder rotation
      local box = uetorch.GetActorBounds(o).boxY

      -- stay in the bounds
      if bounds then
         p.location.x = math.max(bounds.xmin, p.location.x)
         p.location.x = math.min(bounds.xmax, p.location.x)
         p.location.y = math.max(bounds.ymin, p.location.y)
         p.location.y = math.min(bounds.ymax, p.location.y)
      end

      material.set_actor_material(o, p.material)
      uetorch.SetActorScale3D(o, p.scale.x, p.scale.y, p.scale.z)

      if p.start_position == 'up' then
         uetorch.SetActorRotation(o, 0, p.rotation, 0)
         uetorch.SetActorLocation(o, p.location.x, p.location.y, 20)
      else -- down
         uetorch.SetActorRotation(o, 0, p.rotation, 90)
         uetorch.SetActorLocation(o, p.location.x, p.location.y, 20 + box)
      end

      -- register the new occluder as active in the scene
      active_occluders[occluder_name] = o
      noccluders = noccluders + 1

      -- register the occluder for motion (through the occluder.tick
      -- method). If movement==0, the occluder remains static and do
      -- nothing on ticks.
      if p.movement > 0 then
         table.insert(
            mobile_occluders, {
               id=occluder_name:gsub('^.*_', ''),
               mesh=o,
               box=box,
               scale=p.scale,
               rotation=p.rotation,
               movement=p.movement,
               pause=p.pause,
               status='pause',
               t_rotation=0,
               t_rotation_change=0})
      end
   end

   -- destroy the actors not parametrized: for all active actors in
   -- the bank, if it is not an active actor, destroy it
   for _, actor in pairs(occluder_actors) do
      if not is_active_occluder(actor) then
         uetorch.DestroyActor(actor)
      end
   end

   -- register the tick method for occluders rotation (if we have
   -- rotating occluders)
   if mobile_occluders ~= {} then
      tick.add_hook(M.tick, 'fast')
   end
end


-- Return an occluder actor from its name e.g. occluder_1
function M.get_occluder(name)
   local idx = name:gsub('^.*_', '')
   return assert(occluder_actors[tonumber(idx)])
end


-- Return the table (name -> actor) of the active occluders
--
-- Active occluders are those initialized from parameters
function M.get_active_occluders()
   return active_occluders
end


-- Return the number of active occluders
function M.get_noccluders()
   return noccluders
end


function M.tick()
   for _, occluder in pairs(mobile_occluders) do
      if occluder.movement > 0 then
         if occluder.status == 'pause' then
            _occluder_pause(occluder)
         elseif occluder.status == 'go_down' then
            _occluder_move(occluder, -1, 1)
         else -- 'go_up'
            _occluder_move(occluder, 1, 1)
         end
      end
   end
end


function M.get_random_occluder_parameters(name, subblock)
   -- index of the occluder we are generating parameters for
   local idx = name:gsub('occluder_', '')
   idx = tonumber(idx)

   local params = {}
   params.material = material.random('wall')

   -- for train, occluders are fully random
   if subblock:match('train') then
      local shift = {0, 500}
      params.location = {x = shift[idx] - 300, y = -150 - shift[idx]}

      -- Rotation around the Z axis in degree
      params.rotation = math.random(-45, 45)

      params.scale = {x = math.random() + 0.5, y = 1, z = 1.5 - 0.3 * math.random()}

      -- Start position is randomly 'up' or 'down'
      params.start_position = (math.random(0, 1) == 1 and 'up' or 'down')

      -- Select random motion steps for the occluder (0 -> no motion,
      -- 0.5 -> single one way, 1 -> one round trip, 1.5 -> one round
      -- trip and a half, 2 -> two round trips)
      params.movement = math.random(0, 4) / 2

      -- a brief pause between each movement steps
      params.pause = {}
      for i=1, params.movement*2 do
         table.insert(params.pause, math.random(50))
      end

      return params
   end

   -- we are generating occluders for test iterations, with a more
   -- controlled variability
   params.movement = 1
   params.rotation = 0
   params.start_position = 'down'
   params.pause = {math.random(5), math.random(5)}
   params.scale = {x = 0.5, y = 1, z = 1 - 0.4 * math.random()}

   -- occluder's location depends on subblock
   if subblock:match('dynamic_2') then
      local x = {-100, 200}
      params.location = {x = x[idx], y = -350}
   elseif subblock:match('dynamic_1') then
      params.location = {x = 50, y = -250}
   else
      assert(subblock:match('static'))
      params.pause = {5 + math.random(20), math.random(20)}
      params.location = {x = 100 - 200 * params.scale.x, y = -350}
   end

   return params
end


return M
