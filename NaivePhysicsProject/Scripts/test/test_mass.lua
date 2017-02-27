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

local check_overlap = require 'check_overlap'


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
      location = {x = -100, y = -300, z = 70},
      force = {x = 0, y = 0, z = 0}}

   p.actors.sphere_2 = {
      mass_scale = 1,
      material = 'Actor/GreenMaterial',  --material.random('actor'),
      scale = 1,
      location = {x = 50, y = -300, z = 70},
      force = {x = 3e6, y = 0, z = 0}}

   p.actors.sphere_3 = {
      mass_scale = 10000,
      material = material.random('actor'),
      scale = 1,
      location = {x = 300, y = -300, z = 70},
      force = {x = 0, y = 0, z = 0}}

   return p
end


local function on_hit_hook(actor1, actor2)
   if actor1 == 'Sphere_2' and actor2 == 'Sphere_1' then
      uetorch.SetNotifyRigidBodyCollision(actors.get_active_actors()['sphere_2'], false)
      uetorch.SetMassScale(actors.get_active_actors()['sphere_3'], 0.001)
   end
end


function M.initialize(subblock, iteration, params)
   -- camera in test position
   camera.initialize(camera.get_default_parameters())

   -- detect hits on the sphere_2
   uetorch.SetNotifyRigidBodyCollision(actors.get_active_actors()['sphere_2'], true)

   -- register the hook to be triggered on actors hit events
   table.insert(check_overlap.hit_hooks, on_hit_hook)
end


function M.get_main_actor() return nil end
function M.get_occlusion_check_iterations() return {} end
function M.is_test_valid() return false end


return M
