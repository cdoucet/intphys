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
local utils = {}


function utils.GetCurrentIteration()
   local iteration = torch.load(conf.dataPath .. 'iterations.t7')
   return iteration
end


local function GetFirstIterationInBlock(iteration)
   local iterationId, iterationType, block = config.GetIterationInfo(iteration)
   return iteration - config.GetBlockSize(block) + iterationType
end


function utils.UpdateIterationsCounter(check)
   local iteration = utils.GetCurrentIteration()
   local iterationId, iterationType, iterationBlock, iterationPath
      = config.GetIterationInfo(iteration)

   if check then
      iteration = iteration + 1
   else
      print('check failed, trying new parameters')
      iteration = GetFirstIterationInBlock(iteration)
   end

   -- ensure the iteration exists in iterationsTable
   if not iterationsTable[tonumber(iteration)] then
      print('no more iteration, exiting')
      uetorch.ExecuteConsoleCommand('Exit')
   end

   torch.save(conf.dataPath .. 'iterations.t7', iteration)
end


return utils
