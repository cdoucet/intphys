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
local json = require 'dkjson'
local config = {}


-- Pad a number `int` with `n` beginning zeros, return it as a string
--
-- PadZeros(0, 3)  -> '000'
-- PadZeros(12, 3) -> '012'
-- PadZeros(12, 1) -> '12'
function PadZeros(int, n)
   s = tostring(int)
   for _ = 1, n - #s do
      s = '0' .. s
   end
   return s
end


-- Load a JSon file as a table
function ReadJson(file)
   local f = assert(io.open(file, "rb"))
   local content = f:read("*all")
   f:close()
   return json.decode(content)
end


-- Write a table as a JSon file
--
-- `keyorder` is an optional array to specify the ordering of keys in
-- the encoded output. If an object has keys which are not in this
-- array they are written after the sorted keys.
function WriteJson(t, file, keyorder)
   local f = assert(io.open(file, "wb"))
   if keyorder then
      f:write(json.encode(t, {indent = true, level = 1, keyorder = keyorder}))
   else
      f:write(json.encode(t, {indent = true, level = 1}))
   end
   f:close()
end


-- Return the location and rotation of an actor in a string
--
-- The returned string is formatted as:
--   'x y z pitch yaw roll'
function coordinates_to_string(actor)
   local l = uetorch.GetActorLocation(actor)
   local r = uetorch.GetActorRotation(actor)

   return (l.x .. ' ' .. l.y .. ' ' .. l.z .. ' ' ..
              r.pitch .. ' ' .. r.yaw .. ' ' .. r.roll)
end


-- Return unique elements of `t` (equivalent to set(t) in
-- Python). From https://stackoverflow.com/questions/20066835
function unique(t)
   local hash, res = {}, {}
   t:apply(
      function(x) if not hash[x] then res[#res+1] = x; hash[x] = true end end)
   return res
end


conf = {
   dataPath = assert(os.getenv('NAIVEPHYSICS_DATA')),
   loadParams = false,
   captureInterval = {
      blockC1_train = 2,
      blockC1_static = 2,
      blockC1_dynamic_1 = 2,
      blockC1_dynamic_2 = 2
   },
   sceneTicks = {
      blockC1_train = 201,
      blockC1_static = 201,
      blockC1_dynamic_1 = 201,
      blockC1_dynamic_2 = 201
   },
   visibilityCheckSize = {
      blockC1_static = 1,
      blockC1_dynamic_1 = 1,
      blockC1_dynamic_2 = 2,
   },
   tupleSize = {
      blockC1_train = 1,
      blockC1_static = 4,
      blockC1_dynamic_1 = 4,
      blockC1_dynamic_2 = 4,
   },
   blocks = ReadJson(assert(os.getenv('NAIVEPHYSICS_JSON')))
}


function SetIterationsCounter()
   -- count the number of iterations both for train and test. Each
   -- train is always a single iteration, the number of test
   -- iterations depends on the block type
   local train_runs, test_runs, test_iterations = 0, 0, 0
   for block, iters in pairs(config.GetBlocks()) do
      for subblock, nb in pairs(iters) do
         if string.match(subblock, 'train') then
            train_runs = train_runs + nb
         else
            test_runs = test_runs + nb
         end
      end
   end

   if test_runs + train_runs == 0 then
      print('no iterations specified, exiting')
      uetorch.ExecuteConsoleCommand('Exit')
      return
   end
   print("generation of " .. test_runs .. " test and " .. train_runs .. " train samples")
   print("write data to " .. conf.dataPath)

   -- put the detail of each iteration into a table
   local n, id_train, id_test, iterationsTable = 1, 1, 1, {}
   for block, iters in pairs(config.GetBlocks()) do
      for subblock, nb in pairs(iters) do
         local blockName = block .. '_' .. subblock

         -- setup train iterations for the current block
         if string.match(subblock, "train") then
            for id = 1, nb do
               iterationsTable[n] = {
                  iterationBlock=blockName, iterationType=-1, iterationId=id_train}
               n = n + 1
               id_train = id_train + 1
            end
         else
            -- setup test iterations for the current block
            local ntypes = config.GetTupleSize(blockName) + config.GetVisibilityCheckSize(blockName)
            for id = 1, nb do
               for t = ntypes, 1, -1 do
                  iterationsTable[n] = {iterationBlock=blockName, iterationType=t, iterationId=id_test}
                  n = n + 1
               end
               id_test = id_test + 1
            end
         end
      end
   end

   WriteJson(iterationsTable, conf.dataPath .. 'iterations_table.json')
   torch.save(conf.dataPath .. 'iterations.t7', "1")
end


function config.GetDataPath()
   return conf.dataPath
end


function config.GetLoadParams()
   return conf.loadParams
end


function config.GetBlockCaptureInterval(block)
   return conf.captureInterval[block]
end


function config.GetBlockTicks(block)
   return conf.sceneTicks[block]
end


function config.GetBlocks()
   return conf.blocks
end


function config.GetTupleSize(block)
   return conf.tupleSize[block]
end


function config.GetVisibilityCheckSize(block)
   return conf.visibilityCheckSize[block]
end


function config.GetBlockSize(block)
   return conf.visibilityCheckSize[block] + conf.tupleSize[block]
end


function config.IsVisibilityCheck(block, iterationType)
   if conf.visibilityCheckSize[block] == 0 then
      return false
   end
   if iterationType > conf.tupleSize[block] then
      return true
   else
      return false
   end
end


iterationsTable = nil
local maxId = nil

function config.GetIterationInfo(iteration)
   -- if not loaded, load the table of all iterations to execute
   if not iterationsTable then
      iterationsTable = ReadJson(conf.dataPath .. 'iterations_table.json')
      maxId = 0
      for k, v in pairs(conf.blocks) do
         for kk, vv in pairs(v) do
            maxId = math.max(maxId, vv)
         end
      end
   end

   -- retrieve the current iteration in the table
   local i = assert(iterationsTable[tonumber(iteration)])

   -- get the output directory for that iteration
   if i.iterationType == -1 then
      subpath = 'train/'
   else
      subpath = 'test/'
   end

   path = conf.dataPath .. subpath
      .. PadZeros(i.iterationId, #tostring(maxId))
      .. '_' .. i.iterationBlock .. '/'

   if i.iterationType ~= -1 then
      path = path .. i.iterationType .. '/'
   end

   return i.iterationId, i.iterationType, i.iterationBlock, path
end


-- return a string to be printed on screen, describing to humans the
-- iteration being ran, e.g. "running test 1 (2/5) (blockC1_dynamic_1,
-- 120 ticks)"
function config.IterationDescription(iterationBlock, iterationId, iterationType)
   local _type = 'train ' .. iterationId
   if iterationType ~= -1 then
      local _n = 1 + config.GetBlockSize(iterationBlock) - iterationType
      _type = 'test ' .. iterationId ..
         ' (' .. _n .. '/' .. config.GetBlockSize(iterationBlock) .. ')'
   end
   return _type .. ' (' .. iterationBlock .. ')'
end


return config
