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


-- This module defines a test configuration for the block C1: two
-- changes and two occluders, with moving spheres.

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

local block = {}
block.actors = {}

local iterationId, iterationType, iterationBlock, iterationPath
local params = {}
local isHidden1,isHidden2

local visible1 = true
local visible2 = true
local possible = true
local trick1 = false
local trick2 = false

local tCheck, tLastCheck = 0, 0
local step = 0

local function Trick(dt)
   if tCheck - tLastCheck >= config.GetBlockCaptureInterval(iterationBlock) then
      step = step + 1

      if params.spheres['sphere_' .. params.index].side == 'left' then
         if not trick1 and isHidden1[step] then
            trick1 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible2)
         end

         if trick1 and not trick2 and isHidden2[step] then
            trick2 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible1)
         end
      else
         if not trick1 and isHidden2[step] then
            trick1 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible2)
         end

         if trick1 and not trick2 and isHidden1[step] then
            trick2 = true
            uetorch.SetActorVisible(spheres.get_sphere(params.index), visible1)
         end
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
      or (not possible and visible1 and not trick1 and not trick2) -- visible 1st third
      or (not possible and visible2 and trick1 and not trick2) -- visible 2nd third
      or (not possible and visible1 and trick1 and trick2) -- visible 3rd third
   then
      table.insert(active, mainActor)
   else
      table.insert(inactive, mainActor)
   end

   return active, inactive, text
end


function block.MaxActors()
   local max = 3 -- floor + 2 occluders
   if params.backwall.is_active then
      max = max + 1
   end
   return max + params.spheres.n_spheres
end


-- Return random parameters for the C1 dynamic_2 block
local function GetRandomParams()
   local params = {}

   -- spheres
   params.spheres = {}
   params.spheres.n_spheres = spheres.random_n_spheres()
   for i = 1, params.spheres.n_spheres do
      local p = {}

      p.material = spheres.random_material()
      p.scale = 0.9
      p.is_static = false
      p.side = spheres.random_side()
      p.location = {
         x = -400,
         y = -550 - 150 * (i - 1),
         z = 70 + math.random(200)}
      p.force = {
         x = 1.6e6,
         y = 0,
         z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

      if p.side == 'right' then
         p.location.x = 700
         p.force.x = -1 * p.force.x
      end

      params.spheres['sphere_' .. i] = p
   end
   params.index = math.random(1, params.spheres.n_spheres)

   -- occluders
   params.occluders = {}
   params.occluders.n_occluders = 2
   params.occluders.occluder_1 = {
      material = occluders.random_material(),
      movement = 1,
      scale = {x = 0.5, y = 1, z = 1 - 0.4 * math.random()},
      location = {x = -100, y = -350},
      rotation = 0,
      start_position = 'down',
      pause = {math.random(5), math.random(5)}}

   params.occluders.occluder_2 = {
      material = occluders.random_material(),
      movement = 1,
      scale = params.occluders.occluder_1.scale,
      location = {x = 200, y = -350},
      rotation = 0,
      start_position = 'down',
      pause = {table.unpack(params.occluders.occluder_1.pause)}}

   -- others
   params.floor = floor.random()
   params.light = light.random()
   params.backwall = backwall.random()

   return params
end


function block.SetBlock(currentIteration)
   iterationId, iterationType, iterationBlock, iterationPath =
      config.GetIterationInfo(currentIteration)

   if iterationType == 6 then
      if config.GetLoadParams() then
         params = ReadJson(iterationPath .. '../params.json')
      else
         params = GetRandomParams()
         WriteJson(params, iterationPath .. '../params.json')
      end

      uetorch.DestroyActor(occluders.get_occluder(2))
   else
      params = ReadJson(iterationPath .. '../params.json')

      if iterationType == 5 then
         uetorch.DestroyActor(occluders.get_occluder(1))
      else
         isHidden1 = torch.load(iterationPath .. '../hidden_6.t7')
         isHidden2 = torch.load(iterationPath .. '../hidden_5.t7')
         utils.AddTickHook(Trick)

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
   end

   if iterationType == 5 or iterationType == 6 then
      for i = 1, params.spheres.n_spheres do
         if i ~= params.index then
            uetorch.DestroyActor(spheres.get_sphere(i))
         end
      end
   end

   mainActor = spheres.get_sphere(params.index)
   block.actors['occluder_1'] = occluders.get_occluder(1)
   block.actors['occluder_2'] = occluders.get_occluder(2)
   for i = 1,params.spheres.n_spheres do
      block.actors['sphere_' .. i] = spheres.get_sphere(i)
   end
end

function block.RunBlock()
   -- camera, floor, lights and background wall
   camera.setup(iterationType, 150)
   floor.setup(params.floor)
   light.setup(params.light)
   backwall.setup(params.backwall)
   occluders.setup(params.occluders)
   spheres.setup(params.spheres)

   uetorch.SetActorVisible(mainActor, visible1)
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
   local file = io.open(config.GetDataPath() .. 'output.txt', "a")

   if iterationType == 6 then
      local isHidden1 = torch.load(iterationPath .. '../hidden_6.t7')
      local foundHidden = false
      for i = 1,#isHidden1 do
         if isHidden1[i] then
            foundHidden = true
         end
      end

      if not foundHidden then
         file:write("Iteration check failed on condition 1: not hidden in visibility check 1\n")
         status = false
      end
   end

   if iterationType == 5 then
      local isHidden2 = torch.load(iterationPath .. '../hidden_5.t7')
      local foundHidden = false
      for i = 1,#isHidden2 do
         if isHidden2[i] then
            foundHidden = true
         end
      end

      if not foundHidden then
         file:write("Iteration check failed on condition 1: not hidden in visibility check 2\n")
         status = false
      end
   end

   if iterationType < 6 and status then
      local iteration = utils.GetCurrentIteration()
      local ticks = config.GetBlockTicks(iterationBlock)
      local prevData = torch.load(iterationPath .. '../check_' .. (iterationType + 1) .. '.t7')

      for t = 1, ticks do
         -- check location values
         if(math.abs(checkData[t].location.x - prevData[t].location.x) > maxDiff) then
            status = false
         end
         if(math.abs(checkData[t].location.y - prevData[t].location.y) > maxDiff) then
            status = false
         end
         if(math.abs(checkData[t].location.z - prevData[t].location.z) > maxDiff) then
            status = false
         end
         -- check rotation values
         if(math.abs(checkData[t].rotation.pitch - prevData[t].rotation.pitch) > maxDiff) then
            status = false
         end
         if(math.abs(checkData[t].rotation.yaw - prevData[t].rotation.yaw) > maxDiff) then
            status = false
         end
         if(math.abs(checkData[t].rotation.roll - prevData[t].rotation.roll) > maxDiff) then
            status = false
         end
      end

      if not status then
         file:write("Iteration check failed on condition 2\n")
      end
   end

   if not status then
      file:write("Iteration check failed\n")
   elseif iterationType == 1 then
      file:write("Iteration check succeeded\n")
   end

   file:close()
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
