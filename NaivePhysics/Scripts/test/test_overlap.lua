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
local occluders = require 'occluders'
local material = require 'material'
local camera = require 'camera'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'


local M = {}


local function shot_a_ball_in_the_camera()
   local s = {}
   s.mesh = 'sphere'
   s.material = material.random('actor')
   s.scale = {x = 2, y = 2, z = 2}
   s.location = {x = 150, y = -550, z = 70}
   s.rotation = {pitch = 0, roll = 0, yaw = 0}
   s.force = {x = 0, y = 2e6, z = 0}

   return {object_1 = s}
end


local function put_an_occluder_on_the_camera()
   local o = {
      material = material.random('wall'),
      movement = 1,
      pause = {1, 1},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 100, y = -100, z = 70},
      rotation = 0,
      rotation_speed = 15,
      start_position = 'up'}

   return {occluder_1 = o}
end


local function occluders_overlapping()
   local o1 = {
      material = material.random('wall'),
      movement = 2,
      pause = {10, 10, 10, 10},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 300, y = -500, z = 70},
      rotation = 90,
      rotation_speed = 15,
      start_position = 'up'}

   local o2 = {
      material = material.random('wall'),
      movement = 2,
      pause = {10, 10, 10, 10},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 100, y = -200, z = 70},
      rotation = -90,
      rotation_speed = 15,
      start_position = 'up'}

   return {occluder_1 = o1, occluder_2 = o2}
end


-- -- test do not pass because actors with physics allowed do not
-- -- overlap at spawn time: they are placed by UE with an offset
-- -- avoiding the overlap
-- local function sphere_overlaps_backwall()
--    local b = {
--       is_active = true,
--       material = material.random('wall'),
--       height = 2.5,
--       depth = -300,
--       width = 1500}

--    local s = {
--       material = material.random('actor'),
--       scale = 1,
--       is_static = true,
--       location = {x = 50, y = -300.01, z = 70}}

--    return b, {object_1 = s}
-- end


local tests = {
   function(p) p.objects = shot_a_ball_in_the_camera() end,
   function(p) p.occluders = put_an_occluder_on_the_camera() end,
   function(p) p.occluders = occluders_overlapping() end,
}


local idx_file = config.get_data_path() .. 'test_idx.t7'
local idx


function M.initialize()
   -- camera in test position
   --camera.initialize(camera.get_default_parameters())
end


function M.get_random_parameters()
   if not utils.file_exists(idx_file) then
      idx = 1
   else
      idx = torch.load(idx_file)
   end
   torch.save(idx_file, idx+1)

   local p = {--backwall = backwall.get_random_parameters(),
              floor = floor.get_random_parameters(),
              light = light.get_random_parameters()}

   if idx > #tests then
      uetorch.ExecuteConsoleCommand('Exit')
      --print('failure !!')
      return p
   else
      tests[idx](p)
      return p
   end
end


function M.get_main_object() return nil end
function M.get_occlusion_check_iterations() return {} end
function M.is_test_valid() return true end


return M
