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


-- This module saves screen captures and the status of each actor
-- during a scene execution.
--
-- Screen captures are of 3 kinds (screenshots, depth fields and
-- actors masking wrote in the subdirectories scene, depth and mask
-- respectively). The status is wrote as a status.json file.

local uetorch = require 'uetorch'
local image = require 'image'
local paths = require 'paths'

--local backwall = require 'backwall'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'


local M = {}

-- A reference to the current iteration
local iteration

-- A reference to the scene being rendered
local scene

-- A table to store scene's status
local t_status

-- Tensors to store raw images of the scene
local t_scene, t_depth, t_masks

-- The maximum depth is estimated during ticking and used to normalize
-- depth images during the final tick
local max_depth


-- Initialize the saver for a given iteration rendered by a given scene
--
-- Setup the output subdirectories for storing scene, depth and masks,
-- register functions for ticking
--
-- ntick is the maximum number of ticks to be saved
function M.initialize(_iteration, _scene, nticks)
   iteration = _iteration
   scene = _scene
   t_status = {}
   max_depth = 0

   -- allocate memory for images
   local nticks = config.get_nticks()
   local resolution = config.get_resolution()
   t_scene = torch.FloatTensor(nticks, 3, resolution.y, resolution.x):contiguous()
   t_depth = torch.FloatTensor(nticks, resolution.y, resolution.x):contiguous()
   t_masks = torch.IntTensor(nticks, resolution.y, resolution.x):contiguous()

   tick.add_hook(M.push_data, 'slow')
   tick.add_hook(M.save_data, 'final')
end


-- Store the scene's current state in memory
--
-- Push the raw scene, mask and depth screenshots to memory (will be
-- post-processed and saved in the final tick).
function M.push_data()
   if not scene.is_valid() then return end

   local idx = tick.get_counter()

   -- save a screenshot of the scene
   assert(uetorch.Screen(t_scene[idx]))

   -- prepare the actors to be segmented for mask image generation. If
   -- the main actor is inactive (during a magic trick), it must be
   -- ignored in mask images
   local segmented_actors = {}
   for _, a in ipairs(scene.get_ordered_actors()) do
      table.insert(segmented_actors, a[2])
   end

   local ignored_actors = {}
   if not config.is_train(iteration) and not scene.is_main_actor_active() then
      local main_actor = scene.get_main_actor()
      ignored_actors = {main_actor}
      for n, a in pairs(segmented_actors) do
         if a == main_actor then
            table.remove(segmented_actors, n)
         end
      end
   end

   -- compute raw depth field and objects segmentation masks
   assert(uetorch.CaptureDepthAndMasks(
             scene.get_camera(),
             segmented_actors, ignored_actors,
             t_depth[idx], t_masks[idx]))

   -- update the max depth
   max_depth = math.max(t_depth[idx]:max(), max_depth)

   -- update the status table
   table.insert(t_status, scene.get_status())
end


-- Postprocess and save scene data accumulated during the ticks
--
-- Save scene images, normalized depth images, masks images (with
-- bacwall actors merged in a single mask) and the status.json file
function M.save_data()
   if not scene.is_valid() then return end

   -- normalize the depth in [0, 1]
   t_depth:div(max_depth)

   -- merge the backwall actors in a single mask and normalize in [0, 1]
   local ordered_actors = scene.get_ordered_actors()
   local nactors = #ordered_actors
   -- if backwall.is_active() then
   --    local ndiff = backwall.get_nactors()
   --    local min_idx, max_idx = backwall.get_indices(ordered_actors)
   --    t_masks[torch.cmul(t_masks:ge(min_idx), t_masks:le(max_idx))] = min_idx
   --    t_masks[t_masks:gt(max_idx)] = t_masks[t_masks:gt(max_idx)] - ndiff + 1
   --    nactors = nactors - ndiff + 1
   -- end
   t_masks = t_masks:float():div(nactors)

   -- map each mask to it's grayvalue index in the mask image
   local grayscale = {{0, 'sky'}}  -- sky is always black
   local mask_names = {}
   for _, a in pairs(ordered_actors) do table.insert(mask_names, a[1]) end
   -- for idx, name in pairs(backwall.get_merged_actors_names(mask_names)) do
   for idx, name in pairs(mask_names) do
      table.insert(grayscale, {math.floor(255 * idx / nactors), name})
   end

   -- save the images as png, a subdirectory per category
   paths.mkdir(iteration.path .. 'mask')
   paths.mkdir(iteration.path .. 'scene')
   paths.mkdir(iteration.path .. 'depth')

   local nframes = #t_status
   for i = 1, nframes do
      -- numeric index in images filenames
      local idx = utils.pad_zeros(i, #tostring(nframes))

      image.save(iteration.path .. 'scene/scene_' .. idx .. '.png', t_scene[i])
      image.save(iteration.path .. 'depth/depth_' .. idx .. '.png', t_depth[i])
      image.save(iteration.path .. 'mask/mask_' .. idx .. '.png', t_masks[i])
   end

   -- get the status header from the scene
   local s = scene.get_status_header()
   s['block'] = iteration.block:gsub('%.', '_')
   s['max_depth'] = max_depth
   s['masks_grayscale'] = grayscale

   --  append it the status table filled during the ticks
   s['frames'] = t_status

   -- write the status.json with ordered keys
   local keyorder = {
      'block', 'possible', 'floor', 'camera', 'lights',
      'max_depth', 'masks_grayscale', 'frames'}
   utils.write_json(s, iteration.path .. 'status.json', keyorder)
end


return M
