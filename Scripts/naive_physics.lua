local uetorch = require 'uetorch'
local lfs = require 'lfs'
local image = require 'image'
local config = require 'config'
local utils = require 'utils'
local block


function SetResolution(dt)
   uetorch.SetResolution(512, 288) -- keep the 16:9 proportion
end


SetResolution()
uetorch.SetTickDeltaBounds(1/8, 1/8)
math.randomseed(os.getenv('NAIVEPHYSICS_SEED') or os.time())


-- functions called from MainMap_CameraActor_Blueprint
GetCurrentIteration = utils.GetCurrentIteration
RunBlock = nil

-- replace uetorch's Tick function
Tick = utils.Tick

local iterationId, iterationType, iterationBlock, iterationPath

local screenTable, depthTable = {}, {}
local tLastSaveScreen = 0
local tSaveScreen = 0
local step = 0

local function SaveScreen(dt)
   if tSaveScreen - tLastSaveScreen >= config.GetBlockCaptureInterval(iterationBlock) then
      step = step + 1

      local file = iterationPath .. 'scene/scene_' .. step .. '.png'
      local i1 = uetorch.Screen()

      if i1 then
         if config.GetStitch() then
            table.insert(screenTable, i1)
         else
            image.save(file, i1)
         end
      end

      file = iterationPath .. 'depth/depth_' .. step .. '.png'
      local camera = uetorch.GetActor("MainMap_CameraActor_Blueprint_C_0")
      local i2 = uetorch.DepthField(camera)

      if i2 then
         if config.GetStitch() then
            table.insert(depthTable, i2)
         else
            image.save(file, i2)
         end
      end

      tLastSaveScreen = tSaveScreen
   end
   tSaveScreen = tSaveScreen + dt
end

local data = {}
local tSaveText = 0
local tLastSaveText = 0

local function SaveStatusToTable(dt)
   local aux = {t = tSaveText}
   if tSaveText - tLastSaveText >= config.GetBlockCaptureInterval(iterationBlock) then
      for k,v in pairs(block.actors) do
         aux[k] = {
            location = uetorch.GetActorLocation(v),
            rotation = uetorch.GetActorRotation(v)
         }
      end
      table.insert(data, aux)

      tLastSaveText = tSaveText
   end
   tSaveText = tSaveText + dt
end

local visibilityTable = {}
local tCheck, tLastCheck = 0, 0
local step = 0
local hidden = false
local isHidden = {}

local function CheckVisibility(dt)
   if tCheck - tLastCheck >= config.GetBlockCaptureInterval(iterationBlock) then
      step = step + 1
      local file = iterationPath .. 'mask/mask_' .. step .. '.png'
      local actors = {block.MainActor()}
      local i2 = uetorch.ObjectSegmentation(actors)

      if i2 then
         if config.GetStitch() then
            table.insert(visibilityTable, i2)
         else
            image.save(file, i2)
         end

         if torch.max(i2) == 0 then
            hidden = true
         else
            hidden = false
         end
      end

      table.insert(isHidden, hidden)
      tLastCheck = tCheck
   end
   tCheck = tCheck + dt
end

local function SaveData()
   if config.IsVisibilityCheck(iterationBlock, iterationType) then
      local nHidden = #isHidden

      for k = 1,nHidden do
         if not isHidden[k] then
            break
         else
            isHidden[k] = false
         end
      end

      for k = nHidden,1,-1 do
         if not isHidden[k] then
            break
         else
            isHidden[k] = false
         end
      end

      torch.save(config.GetDataPath() .. 'hidden_' .. iterationType .. '.t7', isHidden)
   else
      local filename = iterationPath .. 'data_' .. iterationType .. '.txt'
      local file = assert(io.open(filename, "w"))
      file:write("block = " .. iterationBlock .. "\n")

      local possible = block.IsPossible()
      if possible then
         file:write("possible = true\n")
      else
         file:write("possible = false\n")
      end

      local floor = uetorch.GetActor('Floor')
      local bounds = uetorch.GetActorBounds(floor)
      local minx = bounds["x"] - bounds["boxX"]
      local maxx = bounds["x"] + bounds["boxX"]
      local miny = bounds["y"] - bounds["boxY"]
      local maxy = bounds["y"] + bounds["boxY"]
      file:write("minX = " .. minx .. " maxX = " .. maxx ..
                    " minY = " .. miny .. " maxY = " .. maxy .. "\n")

      local nactors = 0
      for k,v in pairs(block.actors) do
         nactors = nactors + 1
      end
      file:write("number of actors = " .. nactors .. "\n")

      for k, v in ipairs(data) do
         file:write("step = " .. k .. "\n")
         file:write("t = " .. v["t"] .. "\n")

         for k2,v2 in pairs(block.actors) do
            file:write("actor = " .. k2 .. "\n")
            local loc = v[k2]["location"]
            file:write("x = " .. loc["x"] .. " y = " .. loc["y"] .. " z = " .. loc["z"] .. "\n")
            local rot = v[k2]["rotation"]
            file:write("pitch = " .. rot["pitch"] ..
                          " roll = " .. rot["roll"] ..
                          " yaw = " .. rot["yaw"] .. "\n")
         end
      end

      file:close()
   end
end

local function SaveStitchedImages()
   if config.IsVisibilityCheck(iterationBlock, iterationType) then
      local filename = iterationPath .. 'mask/mask.png'
      local height = visibilityTable[1]:size(1)
      local width = visibilityTable[1]:size(2)
      local result = torch.IntTensor(height * #visibilityTable, width)

      for k,v in ipairs(visibilityTable) do
         local aux = result:narrow(1, 1 + (k - 1) * height, height)
         aux:copy(v)
      end
      image.save(filename, result)
   else
      local filename = iterationPath .. 'scene/scene.png'
      local height = screenTable[1]:size(2)
      local width = screenTable[1]:size(3)
      local result = torch.Tensor(3, height * #screenTable, width)

      for k,v in ipairs(screenTable) do
         local aux = result:narrow(2, 1 + (k - 1) * height, height)
         aux:copy(v)
      end
      image.save(filename, result)

      filename = iterationPath .. 'depth/depth.png'
      result = torch.FloatTensor(height * #depthTable, width)

      for k,v in ipairs(depthTable) do
         local aux = result:narrow(1, 1 + (k - 1) * height, height)
         aux:copy(v)
      end
      image.save(filename, result)
   end
end

function SetCurrentIteration()
   local currentIteration = utils.GetCurrentIteration()
   iterationId, iterationType, iterationBlock, iterationPath =
      config.GetIterationInfo(currentIteration)
   print('current iteration :', currentIteration, iterationId, iterationType, iterationBlock)

   block = require(iterationBlock)
   block.SetBlock(currentIteration)
   RunBlock = function()
      return block.RunBlock()
   end

   -- create subdirectories for this iteration
   lfs.mkdir(iterationPath .. 'scene')
   lfs.mkdir(iterationPath .. 'mask')
   lfs.mkdir(iterationPath .. 'depth')


   utils.SetTicksRemaining(config.GetBlockTicks(iterationBlock))

   -- tweak to force the first iteration to be at the required
   -- resolution
   utils.AddTickHook(SetResolution)

   if config.IsVisibilityCheck(iterationBlock, iterationType) then
      utils.AddTickHook(CheckVisibility)
   else
      utils.AddTickHook(SaveScreen)
   end
   utils.AddTickHook(SaveStatusToTable)
   utils.AddTickHook(block.SaveCheckInfo)
   utils.AddEndTickHook(SaveData)
   utils.AddEndTickHook(block.Check)
   if config.GetStitch() then
      utils.AddEndTickHook(SaveStitchedImages)
   end
end
