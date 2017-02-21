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

local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'
local backwall = require 'backwall'


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
   max_depth = 0
   t_status = {}

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
-- Write a scene png file and a mask phg file, estimates the global
-- depth maximum, register the current depth and status to memory
-- (will be saved in the final tick).
function M.push_data()
   if not scene.is_valid() then
      return
   end

   local idx = tick.get_counter()

   -- save a screenshot of the scene
   assert(uetorch.Screen(t_scene[idx]))

   -- scene's actors are required for capturing the masks
   local scene_actors, ignored_actors, _ = scene.get_masks()

   -- compute raw depth field and objects segmentation masks
   assert(uetorch.CaptureDepthAndMasks(
      scene.get_camera(), scene_actors, ignored_actors,
      t_depth[idx], t_masks[idx]))

   -- update the max depth
   max_depth = math.max(t_depth[idx]:max(), max_depth)

   -- udate the status table
   table.insert(t_status, scene.get_status())
end


-- Postprocess and save scene data accumulated during the ticks
--
-- Save scene images, normalized depth images, masks images (with
-- bacwall actors merged in a single mask) and the status.json file
function M.save_data()
   if not scene.is_valid() then
      return
   end

   -- normalize the depth in [0, 1]
   t_depth:div(max_depth)

   -- merge the backwall actors in a single mask and normalize in [0, 1]
   if backwall.is_active() then
      local min_idx, max_idx = backwall.get_indices(scene.get_masks())
      t_masks[torch.cmul(t_masks:ge(min_idx), t_masks:le(max_idx))] = min_idx
      t_masks[t_masks:gt(max_idx)] = t_masks[t_masks:gt(max_idx)] - 2
   end
   t_masks = t_masks:float():div(scene.get_nactors())

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

   --  append it the status table filled during the ticks
   s['frames'] = t_status

   -- write the status.json with ordered keys
   local keyorder = {
      'block', 'possible', 'floor', 'camera', 'lights',
      'max_depth', 'masks_grayscale', 'frames'}
   utils.write_json(s, iteration.path .. 'status.json', keyorder)
end


return M
