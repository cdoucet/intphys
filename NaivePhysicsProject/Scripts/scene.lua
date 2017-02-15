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
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'

local check_overlap = require 'check_overlap'
local check_occlusion = require 'check_occlusion'
local check_coordinates = require 'check_coordinates'


local M = {}

local iteration
local block
local params

local actors = {}


function M.initialize(_iteration)
   iteration = _iteration

   -- load the block module for the current iteration
   block = assert(require(iteration.block))

   -- retrieve the parameters filename
   local relative_path = ''
   if not config.is_train(iteration) then
      relative_path = '../'
   end
   local params_file = iteration.path .. relative_path .. 'params.json'

   -- If this the first iteration of this block, generate random
   -- parameters and save them, otherwise load them
   if config.is_first_iteration_of_block(iteration) then
      params = block.get_random_parameters()
      utils.write_json(params, params_file)
   else
      params = assert(utils.read_json(params_file))
   end

   -- setup the camera with a fixed position in test and a more
   -- variable one for training
   local camera_params = camera.get_default_parameters()
   if config.is_train(iteration) then
      camera_params = camera.get_random_parameters()
   end
   camera.setup(camera_params)

   -- setup the static actors
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)

   -- setup the moving actors (if any)
   if params.spheres then
      spheres.setup(params.spheres)

      for i = 1, params.spheres.n_spheres do
         actors['sphere_' .. i] = spheres.get_sphere(i)
      end
   else
      spheres.remove_all()
   end

   -- setup the occluders (if any)
   if params.occluders then
      occluders.setup(params.occluders)

      for i = 1, params.occluders.n_occluders do
         actors['occluder_' .. i] = occluders.get_occluder(i)
      end
   else
      occluders.remove_all()
   end

   -- setup the block (registering any block specific ticking method)
   if block.initialize then
      block.initialize(iteration, params)
   end
   if block.tick then
      tick.add_hook(block.tick, 'slow')
   end
   if block.final_tick then
      tick.add_hook(block.final_tick, 'final')
   end

   -- initialize the overlap check. The scene will fail if any illegal
   -- overlaping between actors is detected (eg some actor hit the
   -- camera, two occluders are overlapping, etc...).
   check_overlap.initialize()

   if not config.is_train(iteration) then
      check_coordinates.initialize(iteration, block.get_main_actor())
   end

   if block.get_occlusion_check_iterations then
      check_occlusion.initialize(
         iteration, block.get_main_actor(),
         block.get_occlusion_check_iterations())
   end
end


-- Return true is the scene has been validated (all checks successful)
--
-- This method should be called only after the final tick (so that all
-- the checks have a definitive status on the scene)
function M.is_valid()
   return check_overlap.is_valid()
      and check_coordinates.is_valid()
      and check_occlusion.is_valid()
end


-- Return the camera actor
function M.get_camera()
   return camera.get_actor()
end


function M.get_actors()
   return actors
end


-- Return the main actor of the scene if defined, otherwise return nil
function M.get_main_actor()
   if block.get_main_actor then
      return block.get_main_actor()
   end
end


-- Return true if iteration is physically possible, false otherwise
function M.is_possible()
   -- if the block doesn't define this function, we assume the scene
   -- is possible (train cases)
   if block.is_possible then
      return block.is_possible()
   end
   return true
end


function M.get_masks()
   local active, inactive, text = {}, {}, {}

   floor.insert_masks(active, text)
   backwall.insert_masks(active, text, params.backwall)
   if params.occluders then
      occluders.insert_masks(active, text, params.occluders)
   end

   if config.is_train(iteration) then
      spheres.insert_masks(active, text, params.spheres)
   else
      -- on test, the main actor only can be inactive (when hidden)
      for i = 1, params.spheres.n_spheres do
         table.insert(text, "sphere_" .. i)
         if i ~= params.index then
            table.insert(active, spheres.get_sphere(i))
         end
      end

      -- We add the main actor as active only when it's not hidden
      local main_actor = M.get_main_actor()
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
   if params.backwall.is_active then
      n = n + 1
   end

   n = n + params.spheres.n_spheres

   if params.occluders then
         n = n + params.occluders.n_occluders
   end

   return n
end


function M.get_status()
   local nactors = M.get_nactors()
   local _, _, actors = M.get_masks()
   actors = backwall.get_updated_actors(actors)

   local masks = {}
   masks[0] = "sky"
   for n, m in pairs(actors) do
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


return M
