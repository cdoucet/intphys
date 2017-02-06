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


-- This modules manages the spheres on the scene: random
-- initialization and setup.

local uetorch = require 'uetorch'
local material = require 'material'

local M = {}


-- Reference to the sphere actors defined in the scene
local sphere_actors = {
   assert(uetorch.GetActor('Sphere_1')),
   assert(uetorch.GetActor('Sphere_2')),
   assert(uetorch.GetActor('Sphere_3'))
}


-- Return the maximal number of spheres in the scene
function M.get_max_spheres()
   return #sphere_actors
end


-- Return a reference to the sphere i (in must be in [1, get_max_spheres()])
function M.get_sphere(i)
   return assert(sphere_actors[i])
end


-- Return a random number of spheres
function M.random_n_spheres()
   return math.random(1, 3)
end


-- Return a random texture for a sphere
function M.random_material()
   return math.random(#material.sphere_materials)
end


-- Return 'left' or 'right' with 50% chance
function M.random_side()
   if math.random(0, 1) == 1 then
      return 'left'
   else
      return 'right'
   end
end


-- Return a random scale coefficient for a sphere
function M.random_scale()
   return math.random() + 1.5
end


-- Return a random location for the sphere `i`
--
-- `i` must be 1, 2 or 3
-- `side` must be 'left' or 'right'
function M.random_location(i, side)
   local l = {
      x = -400,
      y = -550 - 150 * (i - 1),
      z =  70 + math.random(200)
   }

   if side == 'right' then
      l.x = 500
   end

   return l
end


-- Return true or false: 25% chance the sphere don't move
function M.random_static()
   return (math.random() < 0.25)
end


-- Return a random force vector applied to a sphere
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


-- Return random parameters for spheres initialization
--
-- Random number of spheres and, for each sphere, random texture,
-- scale and movement.
function M.random()
   local params = {}

   params.n_spheres = M.random_n_spheres()

   for i = 1, params.n_spheres do
      local p = {}
      local side = M.random_side()

      p.material = M.random_material()
      p.scale = M.random_scale()
      p.location = M.random_location(i, side)
      p.is_static = M.random_static()
      if not p.is_static then
         p.force = M.random_force(side)
      end

      params['sphere_' .. i] = p
   end

   return params
end


-- Insert actor and name in the masking tables
function M.insert_masks(actors, text, params)
   for i = 1, params.n_spheres do
      table.insert(actors, M.get_sphere(i))
      table.insert(text, 'sphere_' .. i)
   end
end


-- Setup the spheres with the given parameters
--
-- `params` must be a table structured as the one returned by spheres.random()
function M.setup(params)
   -- setup the active spheres
   for i = 1, params.n_spheres do
      -- actor and parameters for the current sphere
      local s = M.get_sphere(i)
      local p = params['sphere_' .. i]

      -- setup material, scale and location
      material.set_actor_material(s, material.sphere_materials[p.material])
      uetorch.SetActorScale3D(s, p.scale, p.scale, p.scale)
      uetorch.SetActorLocation(s, p.location.x, p.location.y, p.location.z)

      -- setup force
      if not p.is_static then
         uetorch.AddForce(s, p.force.x, p.force.y, p.force.z)
      end
   end

   -- destroy any inactive sphere
   for i = params.n_spheres + 1, 3 do
      uetorch.DestroyActor(M.get_sphere(i))
   end
end


return M
