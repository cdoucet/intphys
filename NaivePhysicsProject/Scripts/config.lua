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


-- A table containing the iterations registered in the configuration
-- file
iterations_table = nil

-- The maximal index in the iterations table
max_iteration = nil


conf = {
   data_path = assert(os.getenv('NAIVEPHYSICS_DATA')),
   resolution = {x = 288, y = 288}, -- rendered image resolution (in pixels)
   load_params = false,
   ticks_interval = 2,
   ticks_rate = 1/8,
   nticks = 100,
   blocks = utils.read_json(assert(os.getenv('NAIVEPHYSICS_JSON')))
}


function M.get_data_path()
   return conf.data_path
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

function M.get_ticks_rate()
   return conf.ticks_rate
end

function M.get_nticks()
   return conf.nticks
end

function M.get_blocks()
   return conf.blocks
end


function M.get_check_occlusion_size(iteration)
   local name = iteration.block
   if string.find(name, 'visible') or string.find(name, 'train') then
      return 0
   elseif string.find(name, '2$') then
      return 2
   else
      return 1
   end
end


-- Test iterations have a tuple size of 4 (2 possible cases, 2
-- impossible). Train iterations are single shot with a size of 1.
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
      local tmp = utils.read_json(conf.data_path .. 'iterations_table.json')
      iterations_table = tmp.iterations_table
      max_iteration = tmp.max_iteration
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
      .. '_' .. iteration.block:gsub('%.', '_') .. '/'

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
   return _type .. ' (' .. iteration.block:gsub('block_', ''):gsub('%.', '_') .. ')'
end


-- Return the index stored in the file 'iterations.t7'
local _index = nil
function M.get_current_index()
   if not _index then
      _index = torch.load(conf.data_path .. 'iterations.t7')
   end
   return _index
end


-- Return the current iteration from 'iteration.t7' and the iteration table
function M.get_current_iteration()
   local index = M.get_current_index()
   return M.get_iteration(index)
end


function M.prepare_next_iteration(was_valid)
   local index = M.get_current_index()
   if was_valid and index == max_iteration then
      return 0
   end

   if was_valid then
      index = index + 1
   else
      -- rerun the whole scene by coming back to its first iteration
      print('invalid scene, trying new parameters')
      local iteration = M.get_iteration(index)
      if not M.is_train(iteration) then
         index = index - M.get_block_size(iteration) + iteration.type
      end
   end

   -- the number of remaining iterations
   local remaining = max_iteration - index + 1

   if remaining > 0 then
      -- ensure the iteration exists in the iterations table
      assert(iterations_table[tonumber(index)])

      -- save the index of the next iteration
      torch.save(conf.data_path .. 'iterations.t7', index)
   end

   return remaining
end


-- Add a new iteration in the iterations table
function add_iteration(b, t, i)
   table.insert(iterations_table, {block = b, type = t, id = i})
end


local train_runs, test_runs = 0, 0
function add_train_iteration(block, case, nruns)
   local name = block
   if case then
      name = block .. '.' .. case
   end

   for i = 1, nruns do
      train_runs = train_runs + 1
      add_iteration(name, -1, train_runs)
   end
   max_iteration = (max_iteration or 0) + nruns
end


function add_test_iterations(block, case, subblocks)
   for subblock, nruns in pairs(subblocks) do
      local name = block .. '.' .. case .. '_' .. subblock
      local ntypes = 4 + M.get_check_occlusion_size({block = name})
      for i = 1, nruns do
         test_runs = test_runs + 1
         for t = ntypes, 1, -1 do
            add_iteration(name, t, test_runs)
         end
      end
      max_iteration = (max_iteration or 0) + ntypes * nruns
   end
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
function parse_config_file()
   -- clean the global iterations table
   iterations_table = {}

   -- count the number of iterations both for train and test. Each
   -- train is always a single iteration, the number of test
   -- iterations is 4 + number of occlusion checks (depends on the
   -- block type)
   for block, cases in pairs(conf.blocks) do
      -- special case of the test/config.json file configuring the
      -- unit tests
      if string.match(block, 'test.test_') then
         add_train_iteration(block, nil, cases)
      else
         -- we are parsing a usual config file
         for k, v in pairs(cases) do
            if string.match(k, 'train') then
               add_train_iteration(block, k, v)
            else
               add_test_iterations(block, k, v)
            end
         end
      end
   end

   if max_iteration == 0 then
      print('no iterations specified, exiting')
      return uetorch.ExecuteConsoleCommand('Exit')
   end

   print("generation of " .. test_runs + train_runs .. " scenes ("
         .. test_runs .. " for test and " .. train_runs
         .. " for train, total of " .. max_iteration .. ' iterations)')

   utils.write_json(
      {iterations_table = iterations_table, max_iteration = max_iteration},
      conf.data_path .. 'iterations_table.json')
   torch.save(conf.data_path .. 'iterations.t7', "1")
end


-- Change the viewport resolution to the one defined in configuration
function set_resolution()
   local r = M.get_resolution()
   uetorch.ExecuteConsoleCommand("r.setRes " .. r.x .. 'x' .. r.y)
end


return M
