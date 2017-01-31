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

local material = require 'material'
local backwall = require 'backwall'
local occluders = require 'occluders'
local spheres = require 'spheres'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'

local block = {}
block.actors = {}


local iterationId, iterationType, iterationBlock, iterationPath
local params = {}


-- Return true as train blocks are always physically possible
function block.IsPossible()
   return true
end


function block.MaskingActors()
   local active, text = {}, {}

   floor.insert_masks(active, text)
   backwall.insert_masks(active, text, params.backwall)
   occluders.insert_masks(active, text, params.occluders)
   spheres.insert_masks(active, text, params.spheres)

   -- on train, we don't have any inactive actor
   return active, {}, text
end


function block.MaxActors()
   -- spheres + occluders + floor + backwall
   local max = 1 -- floor
   if params.backwall.is_active then
      max = max + 1
   end

   return max + params.spheres.n_spheres + params.occluders.n_occluders
end


-- Return random parameters for the C1 block, training configuration
local function GetRandomParams()
   local params = {}

   params.spheres = spheres.random()
   params.occluders = occluders.random()
   params.floor = floor.random()
   params.backwall = backwall.random()
   params.camera = camera.random()
   params.light = light.random()

   return params
end


function block.SetBlock(currentIteration)
   iterationId, iterationType, iterationBlock, iterationPath =
      config.GetIterationInfo(currentIteration)

   params = GetRandomParams()
   WriteJson(params, iterationPath .. 'params.json')

   for i = 1, params.occluders.n_occluders do
      block.actors['occluder_' .. i] = occluders.get_occluder(i)
   end

   for i = 1, params.spheres.n_spheres do
      block.actors['sphere_' .. i] = spheres.get_sphere(i)
   end
end


function block.RunBlock()
   camera.setup(iterationType, 150, params.camera)
   spheres.setup(params.spheres)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)
   occluders.setup(params.occluders)
end


function block.get_status()
   local max_actors = block.MaxActors()
   local _, _, actors = block.MaskingActors()
   actors = backwall.get_updated_actors(actors)

   local masks = {}
   masks[0] = "sky"
   for n, m in pairs(actors) do
      masks[math.floor(255 * n/ max_actors)] = m
   end

   local status = {}
   status['possible'] = block.IsPossible()
   status['floor'] = floor.get_status()
   status['camera'] = camera.get_status()
   status['lights'] = light.get_status()
   status['masks_grayscale'] = masks

   return status
end


return block
