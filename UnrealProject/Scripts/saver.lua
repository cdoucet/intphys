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
local utils = require 'utils'
local backwall = require 'backwall'


local M = {}

-- A reference to the current iteration
local iteration

-- A reference to the scene being rendered
local scene

-- A table for pushing status during the ticks
local status = {}

-- A table for pushing raw depth fields during the ticks
local depth_images = {}

-- The maximum depth is estimated during ticking and used to normalize
-- depth images during the final tick
local max_depth = 0

-- The size of the id in generated png files (e.g. scene_001.png has a
-- padding size of 3)
local padding_size = 0


-- Initialize the saver for a given iteration rendered by a given scene
--
-- ntick is the maximum number of ticks to be saved
function M.initialize(_iteration, _scene, nticks)
   iteration = _iteration
   scene = _scene
   padding_size = #tostring(nticks) -- 10 -> 2, 100 -> 3, 1000 -> 4

   paths.mkdir(iteration.path .. 'mask')
   paths.mkdir(iteration.path .. 'scene')
   paths.mkdir(iteration.path .. 'depth')
end


-- Save data for the current scene state
--
-- Write a scene png file and a mask phg file, estimates the global
-- depth maximum, register the current depth and status to memory
-- (will be saved in the final tick).
function M.tick(step)
   -- setup the png files to be wrote
   local step_str = utils.pad_zeros(step, padding_size)
   local scene_file = iteration.path .. 'scene/scene_' .. step_str .. '.png'
   local depth_file = iteration.path .. 'depth/depth_' .. step_str .. '.png'
   local mask_file = iteration.path .. 'mask/mask_' .. step_str .. '.png'

   -- save a screenshot of the scene
   image.save(scene_file, assert(uetorch.Screen()))

   -- scene's actors are required for capturing the masks
   local scene_actors, ignored_actors, scene_actors_names = scene.get_masks()

   -- compute raw depth field and objects segmentation masks
   local depth_img, mask_img = uetorch.CaptureDepthAndMasks(
      scene.get_camera(), scene_actors, ignored_actors)

   -- update the max depth and store the depth image (will be
   -- normalized with the global max depth in the final tick)
   max_depth = math.max(depth_img:max(), max_depth)
   depth_images[depth_file] = depth_img

   -- postprocess the mask image in place: merge the backwall
   -- actors in a single mask.
   backwall.group_masks(mask_img, scene_actors, scene_actors_names)

   -- normalize the mask image in [0, 1] and save it
   mask_img = mask_img:float()
   mask_img:apply(function(x) return x / scene.get_nactors() end)
   image.save(mask_file, mask_img)

   -- push the current coordinates of all actors in the status
   local aux = {}
   for k, v in pairs(scene.get_actors()) do
      aux[k] = utils.coordinates_to_string(v)
   end
   status[step] = aux
end


-- Save normalized depth images and the status.json file
function M.final_tick()
   -- normalize the depth field in [0, 1] with the global max depth
   -- computed on the whole scene, and save the images.
   for filename, depth_image in pairs(depth_images) do
      depth_image:apply(function(x) return x / max_depth end)
      image.save(filename, depth_image)
   end

   -- get the status header from the scene and append it the status
   -- table filled during the hook
   local s = scene.get_status()
   s['block'] = iteration.block
   s['max_depth'] = max_depth
   s['steps'] = status

   -- write the status.json with ordered keys
   local keyorder = {
      'block', 'possible', 'floor', 'camera', 'lights', 'max_depth', 'masks_grayscale', 'steps'}
   utils.write_json(s, iteration.path .. 'status.json', keyorder)
end


return M
