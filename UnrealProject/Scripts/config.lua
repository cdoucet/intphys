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


-- This module handles the configuration file and setup the different
-- iterations it includes.
--
-- An `iteration` is a table with the following fields:
--   iteration.id is the index of the iteration in the table
--   iteration.type is -1 for train and >0 for testing
--   iteration.block is the block for that iteration
--   iteration.path is the output directory for that iteration


local uetorch = require 'uetorch'
local utils = require 'utils'

local M = {}


-- Return the sum of values in the table t
local function sum(t)
   local s = 0
   for _, v in pairs(t) do
      s = s + v
   end
   return s
end


-- A table containing the iterations registered in the configuration
-- file
iterations_table = nil

-- The maximal index ni the iterations table
max_iteration = nil


conf = {
   data_path = assert(os.getenv('NAIVEPHYSICS_DATA')),
   resolution = {x = 288, y = 288}, -- rendered image resolution (in pixels)
   load_params = false,
   ticks_interval = 2,
   nticks = 100,
   blocks = utils.read_json(assert(os.getenv('NAIVEPHYSICS_JSON')))
}

function M.get_blocks()
   return conf.blocks
end

function M.get_resolution()
   return conf.resolution
end

function M.get_load_params()
   return conf.load_params
end

function M.get_ticks_interval()
   return conf.ticks_interval
end

function M.get_nticks()
   return conf.nticks
end

function M.get_data_path()
   return conf.data_path
end


function M.get_check_occlusion_size(iteration)
   local name = iteration.block
   if string.find(name, 'visible') or string.find(name, 'train') then
      return 0
   elseif string.find(name, '*2$') then
      return 2
   else
      return 1
   end
end


function M.get_tuple_size(iteration)
   if M.is_train(iteration) then
      return 1
   else
      return 4
   end
end

-- Return the total number of runs needed for a given iteration
--
-- This includes the data generation iteration and, for testing, the
-- visibility checks.
function M.get_block_size(iteration)
   return M.get_check_occlusion_size(iteration) + M.get_tuple_size(iteration)
end


-- Return true if this iteration is a visibility check
function M.is_check_occlusion(iteration)
   if M.get_check_occlusion_size(iteration) == 0 then
      return false
   end
   if iteration.type > M.get_tuple_size(iteration) then
      return true
   else
      return false
   end
end


-- Return true if this iteration is an identity check
function M.is_identity_check(iteration)
   if M.is_train(iteration) then
      return false
   else
      return true
   end
end


-- Return true if the iteration is for training, false for testing
function M.is_train(iteration)
   return iteration.type == -1
end

-- Return true if the iteration is the first one of the block
function M.is_first_iteration_of_block(iteration, with_occlusion_check)
   if with_occlusion_check == nil then
      with_occlusion_check = true
   end

   local is = false
   if with_occlusion_check then
      is = (iteration.type == M.get_block_size(iteration))
   else
      is = (iteration.type == assert(M.get_tuple_size(iteration)))
   end

   return is or M.is_train(iteration)
end


-- Return the iteration at the position `index` in the table
function M.get_iteration(index)
   -- if not loaded, load the table of all iterations to execute
   if not iterations_table then
      iterations_table = utils.read_json(conf.data_path .. 'iterations_table.json')
      max_iteration = 0
      for _, v in pairs(conf.blocks) do
         for _, vv in pairs(v) do
            if type(vv) == "table" then
               vv = sum(vv)
            end
            max_iteration = math.max(max_iteration, vv)
         end
      end
   end

   -- retrieve the current iteration in the table
   local iteration = assert(iterations_table[tonumber(index)])

   -- get the output directory for that iteration
   local subpath = 'test/'
   if iteration.type == -1 then
      subpath = 'train/'
   end

   local path = conf.data_path .. subpath
      .. utils.pad_zeros(iteration.id, #tostring(max_iteration))
      .. '_' .. iteration.block .. '/'

   if iteration.type ~= -1 then
      path = path .. iteration.type .. '/'
   end

   iteration.path = path
   return iteration
end


-- Return a string briefly describing the current iteration
function M.get_description(iteration)
   local _type = 'train ' .. iteration.id
   if iteration.type ~= -1 then
      local _n = 1 + M.get_block_size(iteration) - iteration.type
      _type = 'test ' .. iteration.id ..
         ' (' .. _n .. '/' .. M.get_block_size(iteration) .. ')'
   end
   return _type .. ' (' .. iteration.block .. ')'
end


-- Return the index stored in the file 'iterations.t7'
function M.get_current_index()
   return torch.load(conf.data_path .. 'iterations.t7')
end


-- Return the current iteration from 'iteration.t7' and the iteration table
function M.get_current_iteration()
   local index = M.get_current_index()
   return M.get_iteration(index)
end


function M.update_iterations_counter(check)
   local index = M.get_current_index()
   local iteration = M.get_iteration(index)

   if check then
      index = index + 1
   else
      print('check failed, trying new parameters')
      -- rerun the whole scene by coming back to its first iteration
      index = index - M.get_block_size(iteration) + iteration.type
   end

   -- ensure the iteration exists in the iterations table
   if not iterations_table[tonumber(index)] then
      print('no more iteration, exiting')
      uetorch.ExecuteConsoleCommand('Exit')
   end

   torch.save(conf.data_path .. 'iterations.t7', index)
end



-- Parses the configuration file and setup the iterations
--
-- This function is called directly from UE blueprint at the very
-- beginning of the program execution.
--
-- It parses the configuration file and writes the
-- 'iteration_table.json' file containing the list of all iterations
-- the program will execute. It also initializes the file
-- 'iterations.t7' containing the index of the current iteration at
-- any point in the execution flow.
function set_iterations_counter()
   -- count the number of iterations both for train and test. Each
   -- train is always a single iteration, the number of test
   -- iterations depends on the block type
   local train_runs, test_runs = 0, 0
   for _, block in pairs(conf.blocks) do
      for set, scenarii in pairs(block) do
         if string.match(set, 'train') then
            train_runs = train_runs + scenarii
         else
            test_runs = test_runs + sum(scenarii)
         end
      end
   end

   if test_runs + train_runs == 0 then
      print('no iterations specified, exiting')
      uetorch.ExecuteConsoleCommand('Exit')
      return
   end

   print("generation of " .. test_runs .. " test and " .. train_runs .. " train samples")
   print("write data to " .. conf.data_path)

   -- put the detail of each iteration into a table
   local n, id_train, id_test, iterations_table = 1, 1, 1, {}
   for block, iters in pairs(conf.blocks) do
      for set, scenarii in pairs(iters) do
         local block_name = block .. '_' .. set

         -- setup train iterations for the current block
         if string.match(set, "train") then
            for id = 1, scenarii do
               iterations_table[n] = {
                  block=block_name,
                  type=-1,
                  id=id_train}
               n = n + 1
               id_train = id_train + 1
            end
         else
            for scenario, nb in pairs(scenarii) do
               local scenario_name = block_name .. '_' .. scenario

               -- setup test iterations for the current block
               local ntypes = M.get_tuple_size({type = 1})
                  + M.get_check_occlusion_size({block = scenario_name})
               for id = 1, nb do
                  for t = ntypes, 1, -1 do
                     iterations_table[n] = {
                        block=scenario_name,
                        type=t,
                        id=id_test}
                     n = n + 1
                  end
                  id_test = id_test + 1
               end
            end
         end
      end
   end

   utils.write_json(iterations_table, conf.data_path .. 'iterations_table.json')
   torch.save(conf.data_path .. 'iterations.t7', "1")
end


return M
