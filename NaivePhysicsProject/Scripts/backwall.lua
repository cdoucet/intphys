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
local utils = require 'utils'
local material = require 'material'
local floor = require 'floor'

local wall = {}


local function get_mesh()
   local mesh_path = "StaticMesh'/Game/Meshes/OccluderWall.OccluderWall'"
   return assert(UE.LoadObject(StaticMesh.Class(), nil, mesh_path))
end


local M = {}


-- Generate a random set of attributes for the background wall
--
-- Params:
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

   is_active = true  -- is_active or (math.random() < 0.5)
   if is_active then
      params.xwidth = math.random() * 2500 + 1500
      params.ylocation = math.random() * 600 - 1500
      params.zscale = math.random() * 9 + 1
      params.material = material.random('wall')
   end

   return params
end


-- Setup a background wall configuration from precomputed attributes
--
-- The params must be table structured as the one returned by
-- M.get_random_parameters()
function M.initialize(params, is_train)
   -- when params is empty we do nothing
   if not params or next(params) == nil then return end

   local setup = {}
   setup.back = {
      location = utils.location(-3140, params.ylocation, 0),
      rotation = utils.rotation(0, 0, 0),
      scale = utils.scale(15, 0.75, params.zscale)}

   -- in test blocks, we don't want to have hits between backwall and
   -- actors because it can make the occlusion check to fail
   if is_train then
      setup.left = {
         location = utils.location(-params.xwidth / 2, params.ylocation - 200, 0),
         rotation = utils.rotation(0, 90, 0),
         scale = utils.scale(6, 0.75, params.zscale)}

      setup.right = {
         location = utils.location(params.xwidth / 2, params.ylocation - 200, 0),
         rotation = utils.rotation(0, 90, 0),
         scale = utils.scale(6, 0.75, params.zscale)}
   end

   for n, p in pairs(setup) do
      local actor = assert(uetorch.SpawnStaticMeshActor(get_mesh(), p.location, p.rotation))
      uetorch.SetActorScale3D(actor, p.scale.x, p.scale.y, p.scale.z)
      material.set_actor_material(actor, params.material)
      uetorch.SetActorVisible(actor, true)

      wall['wall_' .. n] = actor
   end
end


-- Destroy the background wall actor
function M.destroy()
   for _, w in pairs(wall) do
      uetorch.DestroyActor(w)
   end

   wall = {}
end


function M.is_active()
   return next(wall) ~= nil
end


-- return the boundary box the backwall, or nil if the backwall is not
-- active
function M.get_actors()
   return wall
end


function M.get_nactors()
   local i = 0
   for _, _ in pairs(M.get_actors()) do
      i = i + 1
   end
   return i
end


-- Return the backwall bounding box as a table {xmin, xmax, ymin, ymax}
function M.get_bounds()
   local b = {}
   local fb = floor.get_status()

   if wall.wall_left then
      b.xmin = uetorch.GetActorLocation(wall.wall_left).x
   else
      b.xmin = fb.minx
   end

   if wall.wall_right then
      b.xmax = uetorch.GetActorLocation(wall.wall_right).x
   else
      b.xmax = fb.maxx
   end

   if wall.wall_back then
      b.ymin = uetorch.GetActorLocation(wall.wall_back).y
   else
      b.ymin = fb.miny
   end

   b.ymax = fb.maxy

   return b
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
