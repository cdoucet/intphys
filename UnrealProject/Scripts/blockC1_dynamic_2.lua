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
local camera = require 'camera'
local block = {}

local floor = uetorch.GetActor('Floor')
local sphere = uetorch.GetActor("Sphere_1")
local sphere2 = uetorch.GetActor("Sphere_2")
local sphere3 = uetorch.GetActor("Sphere_3")
local spheres = {sphere, sphere2, sphere3}
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

      if params.left[params.index] == 1 then
         if not trick1 and isHidden1[step] then
            trick1 = true
            uetorch.SetActorVisible(spheres[params.index], visible2)
         end

         if trick1 and not trick2 and isHidden2[step] then
            trick2 = true
            uetorch.SetActorVisible(spheres[params.index], visible1)
         end
      else
         if not trick1 and isHidden2[step] then
            trick1 = true
            uetorch.SetActorVisible(spheres[params.index], visible2)
         end

         if trick1 and not trick2 and isHidden1[step] then
            trick2 = true
            uetorch.SetActorVisible(spheres[params.index], visible1)
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

   table.insert(active, floor)
   table.insert(text, "floor")

   if params.isBackwall then
      backwall.tableInsert(active, text)
   end

   table.insert(active, occluder.get_occluder(1))
   table.insert(text, "occluder1")

   table.insert(active, occluder.get_occluder(2))
   table.insert(text, "occluder2")

   -- on test, the main actor only can be inactive (when hidden)
   for i = 1, params.n do
      table.insert(text, 'sphere' .. i)
      if i ~= params.index then
         table.insert(active, spheres[i])
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
   if params.isBackwall then
      max = max + 3
   end
   return max + params.n
end


-- Return random parameters for the C1 dynamic_2 block
local function GetRandomParams()
   local params = {
      ground = math.random(#material.ground_materials),
      -- wall1 = math.random(#material.wall_materials),
      -- wall2 = math.random(#material.wall_materials),
      sphere1 = math.random(#material.sphere_materials),
      sphere2 = math.random(#material.sphere_materials),
      sphere3 = math.random(#material.sphere_materials),
      sphereZ = {
         70 + math.random(200),
         70 + math.random(200),
         70 + math.random(200)
      },

      sphereScale = {
         math.random() + 0.5,
         math.random() + 0.5,
         math.random() + 0.5
      },

      forceX = {
         1600000,
         1600000,
         1600000
      },
      forceY = {0, 0, 0},
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
      },

      occluder = {},
      n = math.random(1,3)
   }
   params.index = math.random(1, params.n)

   -- left occluder
   table.insert(params.occluder, {
                   material = occluder.random_material(),
                   movement = 1,
                   scale = {
                      x = 0.5,
                      y = 1,
                      z = 1 - 0.4 * math.random()
                   },
                   location = {
                      x = -100,
                      y = -350
                   },
                   rotation = 0,
                   start_position = 'down',
                   pause = {math.random(5), math.random(5)}})

   -- right occluder
   table.insert(params.occluder, {
                   material = occluder.random_material(),
                   movement = 1,
                   scale = params.occluder[1].scale,
                   location = {
                      x = 200,
                      y = -350
                   },
                   rotation = 0,
                   start_position = 'down',
                   pause = {table.unpack(params.occluder[1].pause)}})

   -- Background wall with 50% chance
   params.isBackwall = (1 == math.random(0, 1))
   if params.isBackwall then
      params.backwall = backwall.random()
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

   if iterationType == 6 then
      if config.GetLoadParams() then
         params = ReadJson(iterationPath .. '../params.json')
      else
         params = GetRandomParams()
         WriteJson(params, iterationPath .. '../params.json')
      end

      uetorch.DestroyActor(occluder.get_occluder(2))
   else
      params = ReadJson(iterationPath .. '../params.json')

      if iterationType == 5 then
         uetorch.DestroyActor(occluder.get_occluder(1))
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

   mainActor = spheres[params.index]
   block.actors['occluder1'] = occluder.get_occluder(1)
   block.actors['occluder2'] = occluder.get_occluder(2)
   for i = 1,params.n do
      block.actors['sphere' .. i] = spheres[i]
   end
end

function block.RunBlock()
   -- camera
   camera.setup(iterationType, 150)

   -- floor
   material.SetActorMaterial(floor, material.ground_materials[params.ground])

   -- background wall
   if params.isBackwall then
      backwall.setup(params.backwall)
   else
      backwall.hide()
   end

   -- occluders
   for i = 1,2 do
      occluder.setup(i, params.occluder[i])
   end
   utils.AddTickHook(occluder.tick)

   -- spheres
   uetorch.SetActorVisible(sphere, visible1)
   material.SetActorMaterial(spheres[1], material.sphere_materials[params.sphere1])
   material.SetActorMaterial(spheres[2], material.sphere_materials[params.sphere2])
   material.SetActorMaterial(spheres[3], material.sphere_materials[params.sphere3])

   for i = 1,params.n do
      uetorch.SetActorScale3D(spheres[i], 0.9, 0.9, 0.9)
      if params.left[i] == 1 then
         uetorch.SetActorLocation(spheres[i], -400, -550 - 150 * (i - 1), params.sphereZ[i])
      else
         uetorch.SetActorLocation(spheres[i], 700, -550 - 150 * (i - 1), params.sphereZ[i])
         params.forceX[i] = -params.forceX[i]
      end

      uetorch.AddForce(
         spheres[i], params.forceX[i], params.forceY[i], params.signZ[i] * params.forceZ[i])
   end
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

      for t = 1,ticks do
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

return block
