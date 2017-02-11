local uetorch = require 'uetorch'
local backwall = require 'backwall'
local floor = require 'floor'
local light = require 'light'
local spheres = require 'spheres'
local occluders = require 'occluders'
local camera = require 'camera'
local config = require 'config'
local tick = require 'tick'
local check_overlap = require 'check_overlap'


local M = {}


local function shot_a_ball_in_the_camera()
   local p = {material = spheres.random_material(),
              scale = 1,
              is_static = false,
              location = {x = 150, y = -550, z = 70},
              force = {x = 0, y = 2e6, z = 0}}
   return {n_spheres = 1, sphere_1 = p}
end


local function put_an_occluder_on_the_camera()
   local o = {material = occluders.random_material(),
              movement = 2,
              pause = {10, 10, 10, 10},
              scale = {x = 1, y = 1, z = 1},
              location = {x = 0, y = -300, z = 70},
              rotation = 0,
              start_position = 'up'}

   return {n_occluders = 1, occluder_1 = o}
end


function M.get_random_parameters()
   local p = {backwall = backwall.random(),
              floor = floor.random(),
              light = light.random()}
   -- p.spheres = shot_a_ball_in_the_camera()
   p.occluders = put_an_occluder_on_the_camera()
   return p
end


function M.initialize(iteration)
   camera.setup()
   check_overlap.initialize()
end


function M.final_tick()
   -- return check_overlap.is_valid()
   return false
end


return M
