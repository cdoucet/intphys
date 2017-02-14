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
   local s = {
      material = spheres.random_material(),
      scale = 1,
      is_static = false,
      location = {x = 150, y = -550, z = 70},
      force = {x = 0, y = 2e6, z = 0}}

   return {n_spheres = 1, sphere_1 = s}
end


local function put_an_occluder_on_the_camera()
   local o = {
      material = occluders.random_material(),
      movement = 2,
      pause = {10, 10, 10, 10},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 100, y = -100, z = 70},
      rotation = 0,
      start_position = 'up'}

   return {n_occluders = 1, occluder_1 = o}
end


local function occluders_overlapping()
   local o1 = {
      material = occluders.random_material(),
      movement = 2,
      pause = {10, 10, 10, 10},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 100, y = -300, z = 70},
      rotation = 60,
      start_position = 'up'}

   local o2 = {
      material = occluders.random_material(),
      movement = 2,
      pause = {10, 10, 10, 10},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 100, y = -300, z = 70},
      rotation = 150,
      start_position = 'up'}

   return {n_occluders = 2, occluder_1 = o1, occluder_2 = o2}
end


local function sphere_overlaps_backwall()
   local b = {
      is_active = true,
      material = backwall.random_material(),
      height = 2.5,
      depth = -300,
      width = 1500}

   local s = {
      material = spheres.random_material(),
      scale = 1,
      is_static = true,
      location = {x = 50, y = -300.01, z = 70}}

   return b, {n_spheres = 1, sphere_1 = s}
end


local function occluder_overlaps_backwall()
   local b = {
      is_active = true,
      material = backwall.random_material(),
      height = 2.5,
      depth = -300,
      width = 1500}

   local o = {
      material = occluders.random_material(),
      movement = 2,
      pause = {10, 10, 10, 10},
      scale = {x = 1, y = 1, z = 1},
      location = {x = 200, y = -100, z = 70},
      rotation = 90,
      start_position = 'up'}

   return b, {n_occluders = 1, occluder_1 = o}
end


function M.get_random_parameters()
   local p = {backwall = backwall.random(),
              floor = floor.random(),
              light = light.random()}

   -- p.spheres = shot_a_ball_in_the_camera()
   -- p.occluders = put_an_occluder_on_the_camera()
   -- p.occluders = occluders_overlapping()
   -- p.backwall, p.occluders = occluder_overlaps_backwall()
    p.backwall, p.spheres = sphere_overlaps_backwall()
   return p
end


function M.initialize(iteration)
   camera.setup(camera.get_default_parameters())
   check_overlap.initialize()
end


function M.final_tick()
   return not check_overlap.is_valid()
end


return M
