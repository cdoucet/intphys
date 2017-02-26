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
   wall_back = assert(uetorch.GetActor("WallBack")),
   wall_left = assert(uetorch.GetActor("WallLeft")),
   wall_right = assert(uetorch.GetActor("WallRight"))
}


local M = {}


-- Generate a random set of attributes for the background wall
--
-- Params:
--
--    is_active (bool): if true, the backwall is active in the scene,
--       if false the backwall is disabled and the method returns nil.
--
--    If is_active is omitted, it is set to true or false with a 50%
--    probability (the wall is randomly absent or present).
--
-- Returns:
--    If the backwall is active, the returned table has the following
--    entries:
--       {material, height, depth, width}
--    Else it returns an empty table
function M.get_random_parameters(is_active)
   local params = {}
   is_active = is_active or (math.random() < 0.5)

   if is_active then
      params.material = material.random('wall')
      params.height = math.random(1, 10) * 0.5
      params.depth = math.random(-1500, -900)
      params.width = math.random(1500, 4000)
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
-- M.get_random_parameters()
function M.initialize(params, is_train)
   -- the params table is empty, destroy the wall and return
   if not params or next(params) == nil then
      is_active = false
      M.destroy()
      return
   end

   is_active = true
   for _, w in pairs(wall) do
      -- material
      material.set_actor_material(w, params.material)

      -- height
      local scale = uetorch.GetActorScale3D(w)
      uetorch.SetActorScale3D(w, scale.x, scale.y, scale.z * params.height)

      -- depth
      local location = uetorch.GetActorLocation(w)
      uetorch.SetActorLocation(w, location.x, params.depth, location.z)
   end

   -- width
   local location = uetorch.GetActorLocation(wall.wall_left)
   uetorch.SetActorLocation(wall.wall_left, -params.width / 2, location.y, location.z)

   local location = uetorch.GetActorLocation(wall.wall_right)
   uetorch.SetActorLocation(wall.wall_right, params.width / 2, location.y, location.z)

   -- in test blocks, we don't want to have hits between backwall and
   -- actors because it can make the occlusion check to fail
   if not is_train then
      uetorch.DestroyActor(wall.wall_left)
      uetorch.DestroyActor(wall.wall_right)
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


-- Return (min, max) indices of bacwall actors in a list of `{name, actor}` pairs
function M.get_indices(actors)
   -- get the indices of the backwall actors in the image (should be 2, 3, 4)
   local min_idx, max_idx = 10e9, 0
   for k, v in ipairs(actors) do
      v = v[2]
      if v == wall.wall_back or v == wall.wall_left or v == wall.wall_right then
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


function M.get_merged_actors_names(names)
   local new_names = {}
   local is_done = false
   for _, v in ipairs(names) do
      if string.match(v, 'wall') then
         if not is_done then
            is_done = true
            table.insert(new_names, 'wall')
         end
      else
         table.insert(new_names, v)
      end
   end
   return new_names
end


return M
