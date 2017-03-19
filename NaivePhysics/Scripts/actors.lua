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


-- This module manages the physics actors in the scene (i.e. the
-- actors submitted to physical laws, such as spheres or cubes). It
-- provides to main functions: p = get_random_parameters() generates
-- parameters and initialize(p) setup the actors in the scene for the
-- given parameters.

local uetorch = require 'uetorch'
local material = require 'material'
local utils = require 'utils'


-- The shapes available as 3D meshes for the physics actors.
local shapes_available = {'sphere', 'cube', 'cone', 'cylinder'}

-- A table (name -> actor) of actors actually active in the scene
local active_actors

local normalized_names, normalized_actors


-- The length of active_actors
local nactors


-- Return true if `shape` is an available shape, false otherwise
local function is_valid_shape(shape)
   local is_valid = false
   for _, s in ipairs(shapes_available) do
      if shape == s then
         is_valid = true
         break
      end
   end
   return is_valid
end


local volume_scale = {sphere = 1, cube = math.pi / 6, cylinder = 2 / 3, cone = 2}


local M = {}


-- Instanciate a UStaticMesh of `shape` and return a reference to it
--
-- return nil if `shape` is not a valid shape
function M.get_mesh(shape)
   if not is_valid_shape(shape) then return nil end

   local Shape = shape:gsub('^%l', string.upper)  -- 'sphere' -> 'Sphere'
   local path = "StaticMesh'/Game/Meshes/" .. Shape .. "." .. Shape .. "'"
   return assert(UE.LoadObject(StaticMesh.Class(), nil, path))
end


-- Return the list of available shapes for the physics actors
function M.get_shapes()
   return shapes_available
end


-- Return a shape different of `shape` choosen among `shapes`
function M.get_different_shape(shape, shapes)
   shapes = shapes or M.get_shapes()
   --print(shapes)

   local other = shapes[math.random(1, #shapes)]
   while other == shape do
      other = shapes[math.random(1, #shapes)]
   end

   --print('diff than ' .. shape .. ' = ' .. other)
   return other
end


-- Return a table of parameters for the given actors
--
-- The returned table has the format (actor_name -> actor_params)
function M.get_random_parameters(t_actors, t_shapes)
   local params = {}

   for i, name in pairs(t_actors) do
      params[name] = M.get_random_actor_parameters(name, t_shapes[i])
   end

   return params
end


-- Initialize scene's physics actors given their names
function M.initialize(actors_name)
   active_actors = {}
   normalized_names = {}
   normalized_actors = {}
   nactors = 0

   for idx, name in ipairs(actors_name) do
      local actor = assert(uetorch.GetActor(name))
      active_actors[name] = actor

      local n = name:gsub('C_.*$', ''):gsub('^%u', string.lower) .. idx
      normalized_names[n] = actor
      normalized_actors[actor] = n

      nactors = nactors + 1
   end
end


-- Destroy a single actor in the scene
function M.destroy_actor(name)
   local a = assert(active_actors[name])
   uetorch.DestroyActor(a)
   active_actors[name] = nil
   normalized_names[normalized_actors[a]] = nil
   normalized_actors[a] = nil
   nactors = nactors - 1
end


-- Return the table (name -> actor) of the active actors
--
-- Active actors are those initialized from parameters
function M.get_active_actors()
   return active_actors
end


function M.get_active_actors_normalized_names()
   return normalized_names
end


function M.get_actor(name)
   return active_actors[name]
end


-- Actors names have a suffix index, this method access actors by
-- ordered indices
function M.get_actor_by_order(idx)
   local s2n = function(s) return tonumber(s:gsub('^.*_', '')) end
   local name = utils.get_index_in_sorted_table(
      M.get_active_actors(), idx, function(a,b) return s2n(a) < s2n(b) end)
   return active_actors[name]
end


-- Return the name of an `actor`, or nil if the actor is not active
function M.get_name(actor)
   for n, a in pairs(M.get_active_actors()) do
      if a == actor then
         return n
      end
   end
   return nil
end


-- Return the number of active actors
function M.get_nactors()
   return nactors
end


-- Return 'left' or 'right' with 50% chance
function M.random_side()
   if math.random(0, 1) == 1 then
      return 'left'
   else
      return 'right'
   end
end


-- Return a random location for the actor `name`
--
-- `name` must be the name of an active actor
-- `side` must be 'left' or 'right'
function M.random_location(name, side)
   local idx = name:gsub('^.*_', '')

   local l = {
      x = -400,
      y = -550 - 150 * (tonumber(idx) - 1),
      z =  70 + math.random(200)
   }

   if side == 'right' then
      l.x = 500
   end

   return l
end


-- Return true or false: 25% chance the actor don't move
function M.random_static()
   return (math.random() < 0.25)
end


-- Return a random force vector to be applied on an actor
function M.random_force(side)
   local sign_z = 2 * math.random(2) - 3 -- -1 or 1

   local f = {
      x = math.random(5e5, 2e6),
      y = math.random(-1e6, 5e5),
      z = sign_z * math.random(8e5, 1e6)
   }

   if side == 'right' then
      f.x = -1 * f.x
   end

   return f
end


function M.random_shape()
   return shapes_available[math.random(1, #shapes_available)]
end


-- Return random parameters for a single actor given its name
function M.get_random_actor_parameters(name, shape)
   local p = {}
   local side = M.random_side()

   p.mesh = (shape or M.random_shape()):gsub('^%l', string.upper)
   p.material = material.random('actor')

   local s = math.random() + 1.5
   p.scale = {x = s, y = s, z = s}

   p.location = M.random_location(name, side)
   p.rotation = {
      pitch = math.random() * 360,
      yaw = math.random() * 360,
      roll = math.random() * 360}

   if M.random_static() then
      p.force = M.random_force(side)
   else
      p.force = {x = 0, y = 0, z = 0}
   end

   return p
end


return M
