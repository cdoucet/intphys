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


-- This module defines possible materials for the ground, the walls
-- and the spheres. It also defines a function setup a given actor
-- with a given material.
local uetorch = require 'uetorch'

local M = {}


M.ground_materials = {
   "M_Basic_Floor",
   "M_Brick_Clay_Beveled",
   "M_Brick_Clay_New",
   "M_Brick_Clay_Old",
   "M_Brick_Cut_Stone",
   "M_Ground_Grass",
   "M_Ground_Gravel",
   "M_Ground_Moss",
   "M_Wood_Floor_Walnut_Polished",
   "M_Wood_Floor_Walnut_Worn",
   "M_Wood_Oak",
   "M_Wood_Pine",
   "M_Wood_Walnut",
   "M_ConcreteTile",
   "M_Concrete_Tiles",
   "M_Floor_01",
   "M_FloorTile_02",
   "M_GroundSand_01",
   "M_SoilMud01",
   "M_SoilSand_01"
}


M.sphere_materials = {
   "BlackMaterial",
   "GreenMaterial",
   "M_ColorGrid_LowSpec",
   "M_Metal_Brushed_Nickel",
   "M_Metal_Burnished_Steel",
   -- "M_Metal_Chrome",
   "M_Metal_Copper",
   "M_Metal_Gold",
   "M_Metal_Rust",
   "M_Metal_Steel",
   "M_Tech_Hex_Tile",
   "M_Tech_Panel",
   "Base_Colour",
   "M_MetalFloor_01",
}


M.wall_materials = {
   "M_Basic_Wall",
   "M_Brick_Clay_Beveled",
   "M_Brick_Clay_New",
   "M_Brick_Clay_Old",
   "M_Brick_Cut_Stone",
   "M_Brick_Hewn_Stone",
   "M_Ceramic_Tile_Checker",
   "M_CobbleStone_Pebble",
   "M_CobbleStone_Rough",
   "M_CobbleStone_Smooth",
   "M_Bricks_1",
   "M_Bricks_2",
   "M_Bricks_3",
   "M_Bricks_4"
}


function M.set_actor_material(actor, id)
   local material_id = "Material'/Game/Materials/" .. id .. "." .. id .. "'"
   local material = UE.LoadObject(Material.Class(), nil, material_id)
   uetorch.SetMaterial(actor, material)
end


return M
