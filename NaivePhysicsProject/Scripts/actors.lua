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

-- The length of active_actors
local nactors

local forces


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


-- Instanciate a UStaticMesh of `shape` and return a reference to it
--
-- return nil if `shape` is not a valid shape
local function get_mesh(shape)
   if not is_valid_shape(shape) then return nil end

   local Shape = shape:gsub('^%l', string.upper)  -- 'sphere' -> 'Sphere'
   local path = "StaticMesh'/Game/Meshes/" .. Shape .. "." .. Shape .. "'"
   return assert(UE.LoadObject(StaticMesh.Class(), nil, path))
end


local volume_scale = {sphere = 1, cube = math.pi / 6, cylinder = 2 / 3, cone = 2}


local M = {}


-- Return the list of available shapes for the physics actors
function M.get_shapes()
   return shapes_available
end


-- Return an actor name of another shape that the given actor
--
-- e.g. 'cylinder_1' -> 'cube_1'
function M.get_other_shape_actor(name, shapes)
   shapes = shapes or M.get_shapes()

   local shape = name:gsub('_.*$', '')
   local idx = name:gsub('^.*_', '')
   local other = shapes[math.random(1, #shapes)]
   while other == shape do
      other = shapes[math.random(1, #shapes)]
   end

   return other .. '_' .. idx
end


-- Return a table of parameters for the given actors
--
-- `t_actors` is a table of (shape -> n). For exemple, the table
--     {'sphere' = 2, 'cube' = 1}) will generate parameters for
--     sphere_1, sphere_2 and cube_3.
--
-- The returned table has the format (actor_name -> actor_params),
-- where actor_params is also a table with the following structure:
--    {material, scale, location={x, y, z}, force={x, y, z}}
function M.get_random_parameters(t_actors)
   local params = {}

   for _, name in pairs(t_actors) do
      assert(M.is_valid_name(name))
      params[name] = M.get_random_actor_parameters(name)
   end

   return params
end


-- Initialize scene's physics actors given their parameters
--
-- Setup the location, scale, force and material of parametrized
-- actors, destroy the unused ones.
--
-- `params` is a table of (actor_name -> actor_params), for exemple as
--     returned by the get_random_parameters() method. Each actor name
--     must be valid and the actor params must have the following
--     structure (where the 'force' entry is optional):
--         {material, scale, location={x, y, z}, force={x, y, z}}
--
-- `bounds` is an optional table of scene boundaries structured as
--     {xmin, xmax, ymin, ymax}. When used, the actors location is
--     forced to be in thoses bounds.
function M.initialize(params, bounds)
   -- when params is empty we do nothing
   if not params or next(params) == nil then return end

   active_actors = {}
   forces = {}
   nactors = 0

   for actor_name, actor_params in pairs(params) do
      local p = actor_params

      -- stay in the bounds
      if bounds then
         p.location.x = math.max(bounds.xmin, p.location.x)
         p.location.x = math.min(bounds.xmax, p.location.x)
         p.location.y = math.max(bounds.ymin, p.location.y)
         p.location.y = math.min(bounds.ymax, p.location.y)
      end
      if not p.rotation then
         p.rotation = utils.rotation(0, 0, 0)
      end

      -- scale normalization factor
      local scale = p.scale
      if p.volume_normalization then
         scale = scale * math.sqrt(volume_scale[actor_name:gsub('_.*$', '')])
      end

      local mesh = get_mesh(actor_name:gsub('_.*$', ''))
      local actor = assert(uetorch.SpawnStaticMeshActor(mesh, p.location, p.rotation))
      uetorch.SetActorScale3D(actor, scale, scale, scale)
      material.set_actor_material(actor, actor_params.material)
      if p.mass_scale then
         uetorch.SetActorMassScale(actor, p.mass_scale)
      end

      --uetorch.SetActorSimulatePhysics(actor, false)
      uetorch.SetActorVisible(actor, true)

      if p.force then
         forces[actor_name] = p.force
      end

      -- register the new actor as active in the scene
      active_actors[actor_name] = actor
      nactors = nactors + 1
   end
end


function M.activate_physics()
   for n, a in pairs(active_actors or {}) do
      uetorch.SetActorSimulatePhysics(a, true)
      local f = forces[n]
      if f then uetorch.AddForce(a, f.x, f.y, f.z) end
   end
end

-- Destroy a single actor in the scene
function M.destroy_actor(name)
   local a = assert(active_actors[name])
   uetorch.DestroyActor(a)
   active_actors[name] = nil
   nactors = nactors - 1
end


-- Destroy all the actors in the scene
function M.destroy()
   for n, _ in pairs(active_actors or {}) do
      M.destroy_actor(n)
   end
end


-- Return true if `name` is a valid name in the actors bank
function M.is_valid_name(name)
   local shape = name:gsub('_.*$', '')
   local idx = name:gsub('^.*_', '')

   if is_valid_shape(shape) then
      return true
   else
      return false
   end
end


-- Return the table (name -> actor) of the active actors
--
-- Active actors are those initialized from parameters
function M.get_active_actors()
   return active_actors
end


function M.get_actor(name)
   return active_actors[name]
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


-- Return random parameters for a single actor given its name
function M.get_random_actor_parameters(name)
   local p = {}
   local side = M.random_side()

   p.material = material.random('actor')
   p.scale = math.random() + 1.5
   p.location = M.random_location(name, side)
   p.rotation = {
      pitch = math.random() * 360,
      yaw = math.random() * 360,
      roll = math.random() * 360}
   if M.random_static() then
      p.force = M.random_force(side)
   end

   return p
end


return M
