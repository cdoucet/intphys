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


-- This module is entry point of the program, it is called from the
-- packaged game.

-- It configures the current iteration scene and run it, managing the
-- random seed, the tick function and data saving (screen captures).

local uetorch = require 'uetorch'
local paths = require 'paths'
local config = require 'config'
local tick = require 'tick'
local utils = require 'utils'
local scene = require 'scene'
local json = require 'dkjson'


local is_valid = true

-- Called at module startup. This function is automatically called
-- when the module is loaded within the level blueprint.
function initialize()
   -- setup the random seed for parameters generation
   local seed = os.getenv('NAIVEPHYSICS_SEED') or os.time()
   math.randomseed(seed)

   -- setup the game resolution
   local res = config.get_resolution()
   uetorch.ExecuteConsoleCommand("r.setRes " .. res.x .. 'x' .. res.y)

   -- parse the input json configuration file
   config.parse_config_file()
end


function get_remaining_ticks()
   return tick.get_ticks_remaining()
end


function get_remaining_iterations()
   return config.get_remaining_iterations()
end


function is_test_iteration()
   return tostring(not config.is_train(config.get_current_iteration()))
end


function get_current_iteration_json()
   is_valid = true

   -- ticking for `nticks`, taking screenshot every `tick_interval` at
   -- a constant `tick rate`, setup the counter to 0
   tick.initialize(
      config.get_nticks(),
      config.get_ticks_interval(),
      config.get_ticks_rate())

   -- retrieve the current iteration and display a little description
   local iteration = config.get_current_iteration()
   local description = 'running ' .. config.get_description(iteration)
   print(description)

   -- create a subdirectory for this iteration
   paths.mkdir(iteration.path)

   -- prepare the scene for the current iteration
   scene.initialize(iteration)

   local params = scene.get_params()
   -- params.occluders = {}
   -- params.occluders.occluder_1 =
   --    {
   --       movement = 0,
   --       pause = {0, 0},
   --       location = {x = 0, y = -500, z = 20},
   --       start_position = "up",
   --       scale = {x = 1, y = 1, z = 1},
   --       rotation_speed = 10,
   --       material = "Wall/M_Brick_Cut_Stone",
   --       rotation = 0
   --    }
   -- params.occluders.occluder_2 =
   --    {
   --       movement = 1,
   --       pause = {0, 0},
   --       location = {x = 450, y = -600, z = 20},
   --       start_position = "up",
   --       scale = {x = 1, y = 1, z = 1},
   --       rotation_speed = 10,
   --       material = "Wall/M_Brick_Cut_Stone",
   --       rotation = 90
   --    }
   -- local camera = require 'camera'
   -- params.camera = camera.get_default_parameters()

   return json.encode(params)
end

function run_iteration()
   tick.run()
end

function terminate_iteration()
   local remaining = config.prepare_next_iteration(is_valid)
   return tostring(remaining)
end


function invalid_scene(reason)
   print('invalid scene: ' .. reason)
   tick.set_ticks_remaining(0)
   is_valid = false
end


function terminate_program()
   print('no more iterations, exiting')
   --uetorch.ExecuteConsoleCommand('Exit')
end


return {initialize = initialize}
