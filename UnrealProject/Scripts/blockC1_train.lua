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

local material = require 'material'
local backwall = require 'backwall'
local occluder = require 'occluder'
local floor = require 'floor'
local light = require 'light'
local camera = require 'camera'

local block = {}

local sphere = uetorch.GetActor("Sphere_1")
local sphere2 = uetorch.GetActor("Sphere_2")
local sphere3 = uetorch.GetActor("Sphere_3")
local spheres = {sphere, sphere2, sphere3}

block.actors = {}

local iterationId, iterationType, iterationBlock, iterationPath
local params = {}


-- Return true as train blocks are always physically possible
function block.IsPossible()
   return true
end


function block.MaskingActors()
   -- on train, we don't have any inactive actor
   local active, inactive, text = {}, {}, {}

   table.insert(active, floor.actor)
   table.insert(text, "floor")

   if params.backwall.is_active then
      backwall.insert_masks(active, text)
   end

   if params.nOccluders >=1 then
      table.insert(active, occluder.get_occluder(1))
      table.insert(text, "occluder_1")
   end

   if params.nOccluders >= 2 then
      table.insert(active, occluder.get_occluder(2))
      table.insert(text, "occluder_2")
   end

   for i = 1, params.n do
      table.insert(active, spheres[i])
      table.insert(text, 'sphere_' .. i)
   end

   return active, inactive, text
end


function block.MaxActors()
   -- spheres + occluders + floor + backwall
   local max = 1 -- floor
   if params.backwall.is_active then
      max = max + 1
   end
   return max + params.n + params.nOccluders
end


-- Return random parameters for the C1 block, training configuration
local function GetRandomParams()
   local params = {
      -- occluders
      nOccluders = math.random(0, 2),

      -- spheres
      n = math.random(1,3),
      sphere1 = math.random(#material.sphere_materials),
      sphere2 = math.random(#material.sphere_materials),
      sphere3 = math.random(#material.sphere_materials),
      sphereZ = {
         70 + math.random(200),
         70 + math.random(200),
         70 + math.random(200)
      },

      -- scale in [3/2, 5/2], keep it a sphere -> scaling in all axes
      sphereScale = {
         math.random() + 1.5,
         math.random() + 1.5,
         math.random() + 1.5
      },

      -- 25% chance the sphere don't move (no force applied)
      sphereIsStatic = {
         math.random(1, 100) <= 25,
         math.random(1, 100) <= 25,
         math.random(1, 100) <= 25
      },

      forceX = {
         math.random(500000, 2000000),
         math.random(500000, 2000000),
         math.random(500000, 2000000)
      },
      forceY = {
         math.random(-1000000, 500000),
         math.random(-1000000, 500000),
         math.random(-1000000, 500000)
      },
      forceZ = {
         math.random(800000, 1000000),
         math.random(800000, 1000000),
         math.random(800000, 1000000)
      },
      signZ = {
         2 * math.random(2) - 3,
         2 * math.random(2) - 3,
         2 * math.random(2) - 3,
      },
      left = {
         math.random(0,1),
         math.random(0,1),
         math.random(0,1),
      }
   }
   params.index = math.random(1, params.n)

   -- Random configuration for floor material, background wall, camera
   -- and lighting
   params.floor = floor.random()
   params.backwall = backwall.random()
   params.camera = camera.random()
   params.light = light.random()

   -- Pick random attributes for each occluder
   params.occluder = {}
   for i=1, params.nOccluders do
      table.insert(params.occluder, occluder.random(i))
   end

   return params
end


function block.SetBlock(currentIteration)
   iterationId, iterationType, iterationBlock, iterationPath =
      config.GetIterationInfo(currentIteration)

   local file = io.open (config.GetDataPath() .. 'output.txt', "a")
   file:write(currentIteration .. ", " ..
                 iterationId .. ", " ..
                 iterationType .. ", " ..
                 iterationBlock .. "\n")
   file:close()

   params = GetRandomParams()
   WriteJson(params, iterationPath .. 'params.json')

   for i = 1, params.nOccluders do
      block.actors['occluder_' .. i] = occluder.get_occluder(i)
   end

   for i = 1, params.n do
      block.actors['sphere_' .. i] = spheres[i]
   end
end


function block.RunBlock()
   -- camera, floor, lights and background wall
   camera.setup(iterationType, 150, params.camera)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)

   -- occluders
   for i = 1,2 do
      if params.occluder[i] == nil then
         occluder.destroy(i)
      else
         occluder.setup(i, params.occluder[i])
      end
   end
   utils.AddTickHook(occluder.tick)

   -- spheres
   uetorch.SetActorVisible(sphere, true)
   material.SetActorMaterial(spheres[1], material.sphere_materials[params.sphere1])
   material.SetActorMaterial(spheres[2], material.sphere_materials[params.sphere2])
   material.SetActorMaterial(spheres[3], material.sphere_materials[params.sphere3])

   for i = 1,params.n do
      if params.left[i] == 1 then
         uetorch.SetActorLocation(spheres[i], -400, -550 - 150 * (i - 1), params.sphereZ[i])
      else
         uetorch.SetActorLocation(spheres[i], 500, -550 - 150 * (i - 1), params.sphereZ[i])
         params.forceX[i] = -params.forceX[i]
      end

      uetorch.SetActorScale3D(
         spheres[i], params.sphereScale[i], params.sphereScale[i], params.sphereScale[i])

      if not params.sphereIsStatic[i] then
         uetorch.AddForce(
            spheres[i], params.forceX[i], params.forceY[i], params.signZ[i] * params.forceZ[i])
      end
   end
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
