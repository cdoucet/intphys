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


-- This module defines the background wall behavior. Random texture,
-- height, width and distance from the camera. The background wall is
-- a U-shaped wall surrounding the scene. It has physics enabled so
-- the spheres can collide to it.

local uetorch = require 'uetorch'
local material = require 'material'


-- true the background wall is currently active, false otherwise
local is_active


-- Componants of the background wall in the Unreal scene
local wall = {
   back = assert(uetorch.GetActor("WallBack")),
   left = assert(uetorch.GetActor("WallLeft")),
   right = assert(uetorch.GetActor("WallRight"))
}


local M = {}


-- Return true or false with the probability `p` for true, default to 0.5
function M.random_active(p)
   p = p or 0.5
   return (math.random() < p)
end


-- Return a random wall texture for the background wall
function M.random_material()
   return math.random(#material.wall_materials)
end


-- Return a random height for the background wall
function M.random_height()
   return math.random(1, 10) * 0.5
end


-- Return a random location on the Y axis
function M.random_depth()
   return math.random(-1500, -900)
end


-- Pick a random width (length of wall.back)
function M.random_width()
   return math.random(1500, 4000)
end


-- Generate a random set of attributes for the background wall
function M.random()
   local params = {}
   params.is_active = M.random_active()

   if params.is_active then
      params.material = M.random_material()
      params.height = M.random_height()
      params.depth = M.random_depth()
      params.width = M.random_width()
   end

   return params
end


-- Destroy the background wall
function M.destroy()
   for _, w in pairs(wall) do
      uetorch.DestroyActor(w)
   end
end


-- Setup a background wall configuration from precomputed attributes
--
-- The params must be table structured as the one returned by
-- M.random()
function M.setup(params, is_train)
   params = params or M.random()

   if not params.is_active then
      is_active = false
      M.destroy()
      return
   end

   is_active = true
   for _, w in pairs(wall) do
      -- material
      material.set_actor_material(w, material.wall_materials[params.material])

      -- height
      local scale = uetorch.GetActorScale3D(w)
      uetorch.SetActorScale3D(w, scale.x, scale.y, scale.z * params.height)

      -- depth
      local location = uetorch.GetActorLocation(w)
      uetorch.SetActorLocation(w, location.x, params.depth, location.z)
   end

   -- width
   local location = uetorch.GetActorLocation(wall.left)
   uetorch.SetActorLocation(wall.left, -params.width / 2, location.y, location.z)

   local location = uetorch.GetActorLocation(wall.right)
   uetorch.SetActorLocation(wall.right, params.width / 2, location.y, location.z)

   -- in test blocks, we don't want to have hits between backwall and
   -- actors because it can make the occlusion check to fail
   if not is_train then
      uetorch.DestroyActor(wall.left)
      uetorch.DestroyActor(wall.right)
   end
end


function M.is_active()
   return is_active
end


-- return the boundary box the backwall, or nil if the backwall is not
-- active
function M.get_actors()
   return wall
end


-- Insert the background wall componants in the masks table
function M.insert_masks(t_actor, t_text)
   if M.is_active() then
     table.insert(t_actor, wall.back)
     table.insert(t_actor, wall.left)
     table.insert(t_actor, wall.right)

     table.insert(t_text, "back_wall")
     table.insert(t_text, "left_wall")
     table.insert(t_text, "right_wall")
   end
end


-- Return (min, max) indices of bacwall actors in a list of `actors`
function M.get_indices(actors)
   -- get the indices of the backwall actors in the image (should be 2, 3, 4)
   local min_idx, max_idx = 10e9, 0
   for k, v in ipairs(actors) do
      if v == wall.back or v == wall.left or v == wall.right then
         if min_idx > k then
            min_idx = k
         end

         if max_idx < k then
            max_idx = k
         end
      end
   end

   return min_idx, max_idx
end


function M.get_updated_actors(names)
   local new_names = {}
   local __done = false
   for _, v in ipairs(names) do
      if string.match(v, 'wall') then
         if not __done then
            __done = true
            table.insert(new_names, 'wall')
         end
      else
         table.insert(new_names, v)
      end
   end
   return new_names
end


return M
