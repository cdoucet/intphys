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


-- This module handles the different materials available for the
-- scene's physics actors, floor and walls (including background wall
-- and occluders).


local uetorch = require 'uetorch'
local paths = require 'paths'


-- We have different materials for actors, wall (back and occluders) and floor
local materials = {actor = {}, floor = {}, wall = {}}

-- Physical materials defines how an actor insteracts with the world:
-- friction, restitution and density.
local physicals = {}


-- Return a reference to a UMaterialInterface instance given it's name
--
-- `name` must be formatted as 'Category/Name'
--     (e.g. 'Wall/M_BasicWall'). The available names are the keys of
--     table returned by the method material.get_materials()
local function get_material(name)
   local suffix = name:gsub('.*/', '')
   local path = "Material'/Game/Materials/" .. name .. '.' .. suffix .. "'"
   return assert(UE.LoadObject(Material.Class(), nil, path))
end


-- Return a reference to a UPhysicalMaterial instance given it's name
--
-- `name` must be formatted as 'Name'
--     (e.g. 'F0R1'). The available names are the keys of
--     table returned by the method material.get_physicals()
local function get_physical(name)
   local path = "PhysicalMaterial'/Game/PhysicalMaterials/" .. name .. '.' .. name .. "'"
   return assert(UE.LoadObject(PhysicalMaterial.Class(), nil, path))
end


local M = {}


-- Return the available materials for a given category
--
-- The `category` must be 'actor', 'floor' or 'wall'
function M.get_materials(category)
   assert(category == 'actor' or category == 'wall' or category == 'floor')

   -- if not already done, read the available materials in the game directory
   if not next(materials[category]) then
      -- the category with first letter upcased
      local Category = category:gsub('^%l', string.upper)

      -- the directory where uasset material files are stored
      local directory = assert(os.getenv('NAIVEPHYSICS_ROOT'))
         .. '/NaivePhysics/Content/Materials/' .. Category

      for f in paths.files(directory, '%.uasset$') do
         table.insert(materials[category], Category .. '/' .. f:gsub('%.uasset$', ''))
      end
   end

   return materials[category]
end


function M.get_physicals()
   if not next(physicals) then
      local directory = assert(os.getenv('NAIVEPHYSICS_ROOT'))
         .. '/NaivePhysics/Content/PhysicalMaterials'

      for f in paths.files(directory, '%.uasset$') do
         table.insert(physicals, '' .. f:gsub('%.uasset$', ''))
      end
   end

   return physicals
end


-- Change the material of an `actor` to be the one specified by `name`
--
-- `actor` is a reference to an actor object in the scene
-- `name` is the name of the material to setup
function M.set_actor_material(actor, name)
   print(uetorch.SetActorMaterial(actor, get_material(name)))
end


function M.set_physical(actor, name)
   uetorch.SetActorPhysicalMaterial(actor, get_physical(name))
end


function M.get_physical_properties(actor)
   return uetorch.GetActorlPhysicalProperties(actor)
end


-- category must be 'floor', 'wall' or 'actor'
function M.random(category)
   if category == 'ground' then
      category = 'floor'
   end

   local m = M.get_materials(category)
   return m[math.random(1, #m)]
end


return M
