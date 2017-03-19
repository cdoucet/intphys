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


local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'

local backwall = require 'backwall'
local occluders = require 'occluders'
local actors = require 'actors'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'

local check_occlusion = require 'check_occlusion'
local check_coordinates = require 'check_coordinates'


-- The current iteration to run
local iteration

-- The block module (required from iteration.block)
local block

-- The scene's parameters
local params


-- Return a table of parameters for the current scene
--
-- If the iteration is the first one of the block, generate random
-- parameters for that block and save it as 'params.json'. Otherwise
-- load them from 'params.json'.
local function init_params(subblock)
   -- retrieve the parameters filename, when we are in test block,
   -- params.json is a directory up
   local relative_path = ''
   if not config.is_train(iteration) then
      relative_path = '../'
   end
   local params_file = iteration.path .. relative_path .. 'params.json'

   -- If this the first iteration of this block, generate random
   -- parameters and save them, otherwise load them
   local params = {}
   if config.is_first_iteration_of_block(iteration) then
      -- choose random parameters for the block actors (occluders, objects)
      params = block.get_random_parameters(subblock, iteration.nactors)

      -- -- choose random parameters for static actors
      params.floor = floor.get_random_parameters()
      params.light = light.get_random_parameters()
      if math.random() >= 0.5 then
         params.backwall = backwall.get_random_parameters(true)
      end

      -- choose parameters for the camera with a fixed position in
      -- test and a more variable one for training
      if config.is_train(iteration) then
         params.camera = camera.get_random_parameters()
      else
         params.camera = camera.get_default_parameters()
      end

      utils.write_json(params, params_file)
   else
      params = assert(utils.read_json(params_file))
   end

   return params
end


-- Return the [xmin, xmax, ymin, ymax] boundaries of the scene when
-- backwall is active, else return nil
local function get_scene_bounds()
   if not backwall.is_active() then
      return nil
   end

   local bounds = backwall.get_bounds()
   bounds.ymax = uetorch.GetActorLocation(camera.get_actor()).y
   return bounds
end


local M = {}



function M.get_params(_iteration)
   iteration = _iteration

   local block_name = iteration.block:gsub('%..*$', '')
   local subblock_name = iteration.block:gsub('^.*%.', '')

   -- special case of unit tests and dev scripts
   if iteration.block:match('^test.test') then
      block_name = iteration.block
      subblock_name = 'train'
   end

   -- load the scene parameters and the block module
   block = assert(require(block_name))
   params = init_params(subblock_name)

   return params
end



function M.initialize(actors_name, params)
   local p = {occluders = {}, objects = {}}
   actors_name = actors_name .. ' '
   local fields = {actors_name:match((actors_name:gsub("[^ ]* ", "([^ ]*) ")))}
   for _, actor in ipairs(fields) do
      if actor:match('Occluder') then
         table.insert(p.occluders, actor)
      elseif actor:match('Backwall') then
         p.backwall = actor
      else
         assert(actor:match('Object'))
         table.insert(p.objects, actor)
      end
   end

   backwall.initialize(p.backwall)
   occluders.initialize(p.occluders)
   actors.initialize(p.objects)

   local subblock_name = iteration.block:gsub('^.*%.', '')
   block.initialize(subblock_name, iteration, params)

   -- on test blocks, we make sure the main actor coordinates
   -- (location and rotation) are strictly comparable over the
   -- different iterations. If not, the scene fails. This is to detect
   -- an issue we have with the packaged game: some videos run slower
   -- than others (seems to append only in packaged, not in editor)
   if not config.is_train(iteration) then
      check_coordinates.initialize(iteration, block.get_main_object())
   end

   -- in tests blocks with occlusion, we have to make sure the main
   -- actor is occluded before applying the magic trick.
   check_occlusion.initialize(
      iteration,
      block.get_main_object(),
      block.get_occlusion_check_iterations(),
      config.get_resolution())
end


-- Return true is the scene has been validated (all checks successful)
--
-- This method should be called only after the final tick (so that all
-- the checks have a definitive status on the scene)
function M.is_valid()
   -- special case for unit tests
   if string.match(iteration.block, 'test.test_') then
      return block.is_test_valid()
   else
      return check_occlusion.is_valid() and check_coordinates.is_valid()
   end
end


-- Return the camera actor
function M.get_camera()
   return camera.get_actor()
end


-- Return the main actor of the scene if defined, otherwise return nil
function M.get_main_actor()
   return block.get_main_object()
end


-- Return true if scene is physically possible, false otherwise
function M.is_possible()
   return block.is_possible()
end


function M.is_main_actor_active()
   if block.is_main_object_active then
      return block.is_main_object_active()
   else
      return true
   end
end


function M.get_active_actors_normalized_names()
   if block.get_active_actors_normalized_names then
      return block.get_active_actors_normalized_names()
   else
      return actors.get_active_actors_normalized_names()
   end
end


function M.get_ordered_actors()
   local ordered = {}

   for name, actor in pairs(floor.get_actor()) do
      table.insert(ordered, {name, actor})
   end
   if backwall.is_active() then
      table.insert(ordered, {'backwall', backwall.get_actor()})
   end

   for name, actor in pairs(occluders.get_occluders_normalized_names()) do
      table.insert(ordered, {name, actor})
   end
   for name, actor in pairs(M.get_active_actors_normalized_names()) do
      table.insert(ordered, {name, actor})
   end

   return ordered
end


-- Return general metadata about the scene and it's static componants
--
-- This function is called at the end of the scene by the saver to
-- write the header of the status.json file
function M.get_status_header()
   local status = {}

   status['possible'] = M.is_possible()
   status['floor'] = floor.get_status()
   status['camera'] = camera.get_status()
   status['lights'] = light.get_status()

   return status
end


-- Return metadata about the dynamic componants of the scene
--
-- This function is called at each tick by the saver to retrieve the
-- current coordinates of all the moving actors in the scene.
function M.get_status()
   local status = {}

   -- the physics actors
   for name, actor in pairs(actors.get_active_actors_normalized_names()) do
      -- don't register the main actor when hidden by a magic trick
      if actor ~= block.get_main_object() or M.is_main_actor_active() then
         status[name] = utils.coordinates_to_string(actor)
      end
   end

   -- the occluders
   for name, actor in pairs(occluders.get_occluders_normalized_names()) do
      status[name] = utils.coordinates_to_string(actor)
   end

   return status
end


return M
