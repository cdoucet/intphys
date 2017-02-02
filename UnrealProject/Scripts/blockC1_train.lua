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


-- This module defines the training configuration for the block C1.

local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'

local material = require 'material'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'

local M = {}
M.actors = {}

local iteration
local params = {}


-- Return true as train blocks are always physically possible
function M.is_possible()
   return true
end


function M.get_masks()
   local active, text = {}, {}

   floor.insert_masks(active, text)
   backwall.insert_masks(active, text, params.backwall)
   occluders.insert_masks(active, text, params.occluders)
   spheres.insert_masks(active, text, params.spheres)

   -- on train, we don't have any inactive actor
   return active, {}, text
end


function M.nactors()
   -- spheres + occluders + floor + backwall
   local max = 1 -- floor
   if params.backwall.is_active then
      max = max + 1
   end

   return max + params.spheres.n_spheres + params.occluders.n_occluders
end


-- Return random parameters for the C1 block, training configuration
local function get_random_parameters()
   local params = {}

   params.spheres = spheres.random()
   params.occluders = occluders.random()
   params.floor = floor.random()
   params.backwall = backwall.random()
   params.camera = camera.random()
   params.light = light.random()

   return params
end


function M.set_block(iteration)
   params = get_random_parameters()
   utils.write_json(params, iteration.path .. 'params.json')

   for i = 1, params.occluders.n_occluders do
      M.actors['occluder_' .. i] = occluders.get_occluder(i)
   end

   for i = 1, params.spheres.n_spheres do
      M.actors['sphere_' .. i] = spheres.get_sphere(i)
   end
end


function M.run_block()
   camera.setup(config.get_current_iteration().type, 150, params.camera)
   spheres.setup(params.spheres)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)
   occluders.setup(params.occluders)
end


function M.get_status()
   local nactors = M.nactors()
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
