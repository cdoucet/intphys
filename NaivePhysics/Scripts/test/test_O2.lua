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


-- This test module is asserting the lua/UE interaction works
-- well. Detection of various overlapping situation in reaction to the
-- events triggered in the MainMap level blueprint

local uetorch = require 'uetorch'
local backwall = require 'backwall'
local floor = require 'floor'
local light = require 'light'
local actors = require 'actors'
local scene = require 'scene'
local occluders = require 'occluders'
local material = require 'material'
local camera = require 'camera'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'


local M = {}


local idx = 1

local meshes = {'cube', 'sphere'}


local function params_dynamic_ice(p)
   local s = {
      scale = 1,
      material = material.random('actor'),
      location = {x = 0, y = -550, z = 70},
      force = {x = 1e6, y = 0, z = 0}}
   p.actors = {}
   p.actors.cube_1 = s
end


local function params_dynamic_parabolic(p)
   local m = 1
   if idx % 2 == 0 then m = 2 end

   local s = {
      scale = utils.location(1, 1, 1),
      material = material.random('actor'),
      mesh = meshes[m],
      location = {x = -200, y = -550, z = 150},
      rotation = utils.rotation(0, 0, 0),
      force = {x = 2.5e6, y = 0, z = 2.7e6}}
   p.objects = {}
   p.objects.object_1 = s
end


-- local function print_velocity(actor)
--    local v = uetorch.GetActorVelocity(actor)
--    local w = uetorch.GetActorAngularVelocity(actor)
--    print(string.format('%f %f %f | %f %f %f',
--                        v.x, v.y, v.z,
--                        w.x, w.y, w.z))
-- end


local tests = {
   --function(p) params_dynamic_ice(p) end,
   function(p) params_dynamic_parabolic(p) end,
}


function M.initialize()
   -- local floor_actor = floor.get_actor().floor
   -- material.set_actor_material(floor_actor, 'M_Ice')
   -- material.set_physical(floor_actor, 'Ice')
   local actor = assert(actors.get_active_actors_normalized_names()['object_1'])

   if idx % 2 == 0 then
      tick.add_hook(
         function()
            --print_velocity(actor)
            if tick.get_counter() == 15 then
               local m = 'sphere'
               if idx == 3 then m = 'cube' end
               uetorch.SetActorStaticMesh(actor, actors.get_mesh(m))
         end end, 'slow')
   end
end


function M.get_random_parameters()
   local p = {}

   if idx > 4 then
      uetorch.ExecuteConsoleCommand('Exit')
      return {}
   else
      tests[1](p)
      idx = idx + 1
      return p
   end
end


function M.get_main_object() return nil end
function M.get_occlusion_check_iterations() return {} end
function M.is_test_valid() return false end


return M
