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


-- A test module asserting the lua/UE interaction works
-- well. Detection of various overlapping situation in reaction to the
-- events triggered in the MainMap level blueprint

local uetorch = require 'uetorch'
local floor = require 'floor'
local light = require 'light'
local actors = require 'actors'
local material = require 'material'
local camera = require 'camera'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'


local M = {}


function M.get_random_parameters()
   local p = {
      floor = floor.get_random_parameters(),
      light = light.get_random_parameters()}

   p.actors = {}
   p.actors.sphere_1 = {
      mass_scale = 100,
      material = material.random('actor'),
      scale = 1,
      location = {x = 0, y = -300, z = 70},
      force = {x = 5e5, y = 0, z = 0}}

   p.actors.sphere_2 = {
      mass_scale = 1,
      material = material.random('actor'),
      scale = 1,
      location = {x = 100, y = -300, z = 70},
      force = {x = 2e6, y = 0, z = 0}}

   p.actors.sphere_3 = {
      mass_scale = 100,
      material = material.random('actor'),
      scale = 1,
      location = {x = 400, y = -300, z = 70},
      force = {x = -5e5, y = 0, z = 0}}

   return p
end


function M.initialize(subblock, iteration, params)
   -- camera in test position
   camera.initialize(camera.get_default_parameters())

   uetorch.SetNotifyRigidBodyCollision(actors.get_active_actors()['sphere_2'], true)

   --print('masses:')
   for name, actor in pairs(actors.get_active_actors()) do
      print(name .. ' : ' .. uetorch.GetMassScale(actor) .. ' ' .. uetorch.GetMass(actor))
   --    --print(name, material.get_physical_properties(params.actors[name].material))
   end
end


function M.get_main_actor() return nil end
function M.get_occlusion_check_iterations() return {} end
function M.is_test_valid() return false end


return M
