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


-- This module defines a test configuration for the block C1: a single
-- change and a single occluder, with moving spheres

local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'

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

local isHidden
local visible1 = true
local visible2 = true
local possible = true
local trick = false

local tCheck, tLastCheck = 0, 0
local step = 0
local function Trick(dt)
   if tCheck - tLastCheck >= config.GetBlockCaptureInterval(iterationBlock) then
      step = step + 1

      if not trick and isHidden[step] then
         trick = true
         uetorch.SetActorVisible(spheres.get_sphere(params.index), visible2)
      end

      tLastCheck = tCheck
   end
   tCheck = tCheck + dt
end


local mainActor
function block.MainActor()
   return mainActor
end


function block.MaskingActors()
   local active, inactive, text = {}, {}, {}

   floor.insert_masks(active, text)
   backwall.insert_masks(active, text, params.backwall)
   occluders.insert_masks(active, text, params.occluders)

   -- on test, the main actor only can be inactive (when hidden)
   for i = 1, params.spheres.n_spheres do
      table.insert(text, 'sphere_' .. i)
      if i ~= params.index then
         table.insert(active, spheres.get_sphere(i))
      end
   end

   -- We add the main actor as active only when it's not hidden
   if (possible and visible1) -- visible all time
      or (not possible and visible1 and not trick) -- visible 1st half
      or (not possible and visible2 and trick) -- visible 2nd half
   then
      table.insert(active, mainActor)
   else
      table.insert(inactive, mainActor)
   end

   return active, inactive, text
end


function block.MaxActors()
   local max = 2 -- floor + occluder
   if params.backwall.is_active then
      max = max + 1
   end
   return max + params.spheres.n_spheres
end


-- Return random parameters for the C1 dynamic_1 block
local function GetRandomParams()
   local params = {}

   -- occluder
   params.occluders = {}
   params.occluders.n_occluders = 1
   params.occluders.occluder_1 = {
      material = occluders.random_material(),
      movement = 1,
      scale = {
         x = 0.5,
         y = 1,
         z = 1 - 0.5 * math.random()},
      location = {
         x = 50,
         y = -250},
      rotation = 0,
      start_position = 'down',
      pause = {math.random(5), math.random(5)}}

   -- spheres
   params.spheres = {}
   params.spheres.n_spheres = spheres.random_n_spheres()
   for i = 1, params.spheres.n_spheres do
      local p = {}

      p.material = spheres.random_material()
      p.scale = 0.9
      p.is_static = false
      p.location = {
         x = -400,
         y = -350 - 150 * (i - 1),
         z = 70 + math.random(200)}
      p.force = {
         x = math.random(800000, 1100000),
         y = 0,
         z = math.random(800000, 1000000) * (2 * math.random(2) - 3)}

      if spheres.random_side() == 'right' then
         p.location.x = 500
         p.force.x = -1 * p.force.x
      end

      params.spheres['sphere_' .. i] = p
   end

   params.index = math.random(1, params.spheres.n_spheres)

   -- others
   params.floor = floor.random()
   params.light = light.random()
   params.backwall = backwall.random()

   return params
end


function block.SetBlock(currentIteration)
   iterationId, iterationType, iterationBlock, iterationPath
      = config.GetIterationInfo(currentIteration)

   if iterationType == 5 then
      if config.GetLoadParams() then
         params = ReadJson(iterationPath .. '../params.json')
      else
         params = GetRandomParams()
         WriteJson(params, iterationPath .. '../params.json')
      end

      for i = 1,3 do
         if i ~= params.index then
            uetorch.DestroyActor(spheres.get_sphere(i))
         end
      end
   else
      isHidden = torch.load(iterationPath .. '../hidden_5.t7')
      params = ReadJson(iterationPath .. '../params.json')
      tick.add_tick_hook(Trick)

      if iterationType == 1 then
         visible1 = false
         visible2 = false
         possible = true
      elseif iterationType == 2 then
         visible1 = true
         visible2 = true
         possible = true
      elseif iterationType == 3 then
         visible1 = false
         visible2 = true
         possible = false
      elseif iterationType == 4 then
         visible1 = true
         visible2 = false
         possible = false
      end
   end

   mainActor = spheres.get_sphere(params.index)
   block.actors.occluder = occluders.get_occluder(1)
   for i = 1, params.spheres.n_spheres do
      block.actors['sphere_' .. i] = spheres.get_sphere(i)
   end
end

function block.RunBlock()
   camera.setup(iterationType, 150)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)
   occluders.setup(params.occluders)
   spheres.setup(params.spheres)

   uetorch.SetActorVisible(spheres.get_sphere(params.index), visible1)
end

local checkData = {}
local saveTick = 1

function block.SaveCheckInfo(dt)
   local aux = {}
   aux.location = uetorch.GetActorLocation(mainActor)
   aux.rotation = uetorch.GetActorRotation(mainActor)
   table.insert(checkData, aux)
   saveTick = saveTick + 1
end

local maxDiff = 1e-6

function block.Check()
   local status = true
   torch.save(iterationPath .. '../check_' .. iterationType .. '.t7', checkData)

   if iterationType == 1 then
      local file = io.open(config.GetDataPath() .. 'output.txt', "a")

      local foundHidden = false
      for i = 1,#isHidden do
         if isHidden[i] then
            foundHidden = true
         end
      end

      if not foundHidden then
         file:write("Iteration check failed on condition 1\n")
         status = false
      end

      if status then
         local iteration = utils.GetCurrentIteration()
         local size = config.GetBlockSize(iterationBlock)
         local ticks = config.GetBlockTicks(iterationBlock)
         local allData = {}

         for i = 1,size do
            local aux = torch.load(iterationPath .. '../check_' .. i .. '.t7')
            allData[i] = aux
         end

         for t = 1,ticks do
            for i = 2,size do
               -- check location values
               if(math.abs(allData[i][t].location.x - allData[1][t].location.x) > maxDiff) then
                  status = false
               end
               if(math.abs(allData[i][t].location.y - allData[1][t].location.y) > maxDiff) then
                  status = false
               end
               if(math.abs(allData[i][t].location.z - allData[1][t].location.z) > maxDiff) then
                  status = false
               end
               -- check rotation values
               if(math.abs(allData[i][t].rotation.pitch - allData[1][t].rotation.pitch) > maxDiff) then
                  status = false
               end
               if(math.abs(allData[i][t].rotation.yaw - allData[1][t].rotation.yaw) > maxDiff) then
                  status = false
               end
               if(math.abs(allData[i][t].rotation.roll - allData[1][t].rotation.roll) > maxDiff) then
                  status = false
               end
            end
         end

         if not status then
            file:write("Iteration check failed on condition 2\n")
         end
      end

      if status then
         file:write("Iteration check succeeded\n")
      else
         file:write("Iteration check failed\n")
      end
      file:close()
   end

   utils.UpdateIterationsCounter(status)
end


function block.IsPossible()
   return possible
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
