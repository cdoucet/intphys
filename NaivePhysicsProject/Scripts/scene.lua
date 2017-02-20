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

local check_overlap = require 'check_overlap'
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
   local params
   if config.is_first_iteration_of_block(iteration) then
      -- choose random parameters for the block actors
      params = block.get_random_parameters(subblock)

      -- choose random parameters for static actors
      params.floor = floor.random()
      params.light = light.random()
      params.backwall = backwall.random()

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

   local wall = backwall.get_actors()
   return {
      xmin = uetorch.GetActorLocation(wall.left).x,
      xmax = uetorch.GetActorLocation(wall.right).x,
      ymin = uetorch.GetActorLocation(wall.back).y,
      ymax = uetorch.GetActorLocation(camera.get_actor()).y}
end


local M = {}


function M.initialize(_iteration)
   iteration = _iteration


   local block_name = iteration.block:gsub('%..*$', '')
   local subblock_name = iteration.block:gsub('^.*%.', '')

   -- load the scene parameters and the block module
   block = assert(require(block_name))
   params = init_params(subblock_name)

   -- setup the camera and static actors. On test blocks, left and
   -- right components of the backwall are disabled to avoid
   -- unexpected collisions
   camera.setup(params.camera)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall, config.is_train(iteration))

   -- retrieve the backwall bounds to make sure all actors are inside
   local bounds = get_scene_bounds()

   -- setup the physics actors and the occluders
   actors.initialize(params.actors, bounds)
   occluders.setup(params.occluders, bounds)

   -- setup the block (registering any block specific ticking method)
   block.initialize(subblock_name, iteration, params)

   -- initialize the overlap check. The scene will fail if any illegal
   -- overlaping between actors is detected (eg some actor hit the
   -- camera, two occluders are overlapping, etc...).
   check_overlap.initialize()

   -- on test blocks, we make sure the main actor coordinates
   -- (location and rotation) are strictly comparable over the
   -- different iterations. If not, the scene fails. This is to detect
   -- an issue we have with the packaged game: some videos run slower
   -- than others (seems to append only in packaged, not in editor)
   if not config.is_train(iteration) then
      check_coordinates.initialize(iteration, block.get_main_actor())
   end

   -- in tests blocks with occlusion, we have to make sure the main
   -- actor is occluded before applying the magic trick.
   check_occlusion.initialize(
      iteration,
      block.get_main_actor(),
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
      return check_overlap.is_valid()
         and check_coordinates.is_valid()
         and check_occlusion.is_valid()
   end
end


-- Return the camera actor
function M.get_camera()
   return camera.get_actor()
end


function M.get_moving_actors()
   local a = {}
   for name, actor in pairs(actors.get_active_actors()) do
      a[name] = actor
   end
   if params.occluders then
      for i = 1, params.occluders.noccluders do
         a['occluder_' .. i] = occluders.get_occluder(i)
      end
   end
   return a
end


-- Return the main actor of the scene if defined, otherwise return nil
function M.get_main_actor()
   return block.get_main_actor()
end


-- Return true if scene is physically possible, false otherwise
function M.is_possible()
   return block.is_possible()
end


function M.get_masks()
   local active, inactive, text = {}, {}, {}


   floor.insert_masks(active, text)
   backwall.insert_masks(active, text)

   if params.occluders then
      for i = 1, params.occluders.noccluders do
         table.insert(text, 'occluder_' .. i)
         table.insert(active, occluders.get_occluder(i))
      end
   end

   if config.is_train(iteration) then
      for name, actor in pairs(actors.get_active_actors()) do
         table.insert(text, name)
         table.insert(active, actor)
      end

   else
      -- on test, the main actor only can be inactive (when hidden)
      for name, actor in pairs(actors.get_active_actors()) do
         table.insert(text, name)
         if name ~= params.main_actor then
            table.insert(active, actor)
         end
      end

      -- We add the main actor as active only when it's not hidden
      local main_actor = block.get_main_actor()
      if block.is_main_actor_visible() then
         table.insert(active, main_actor)
      else
         table.insert(inactive, main_actor)
      end
   end

   return active, inactive, text
end


function M.get_nactors()
   -- spheres + occluders + floor + backwall
   local n = 1 -- floor
   if backwall.is_active() then
      n = n + 1
   end

   n = n + actors.get_nactors()
   if params.occluders then
         n = n + params.occluders.noccluders
   end
   return n
end


function M.get_status()
   local nactors = M.get_nactors()
   local _, _, mask_names = M.get_masks(true)
   mask_names = backwall.get_updated_actors(mask_names)

   local masks = {}
   masks[0] = "sky"
   for n, m in pairs(mask_names) do
      masks[math.floor(255 * n / nactors)] = m
   end

   local status = {}
   status['possible'] = M.is_possible()
   status['floor'] = floor.get_status()
   status['camera'] = camera.get_status()
   status['lights'] = light.get_status()
   status['masks_grayscale'] = masks

   return status
end


function M.clean()
   check_overlap.clean()
end


return M
