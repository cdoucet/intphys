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
local paths = require 'paths'
local utils = require 'utils'


-- from '800x600' to {x = 800, y = 600}
local function parse_resolution(r)
   assert(r:match('^[0-9]+x[0-9]+$'))
   local x = r:gsub('x.*$', '')
   local y = r:gsub('^.*x', '')
   return {x = tonumber(x), y = tonumber(y)}
end


local M = {}



-- A table of iterations registered in the configuration file
local iterations_table

-- The maximal index in the iterations table
local max_iteration

-- The index of the current iteration in the table
local current_index


conf = {
   data_path = assert(os.getenv('NAIVEPHYSICS_DATA')),
   config_file = assert(os.getenv('NAIVEPHYSICS_JSON')),
   resolution = parse_resolution(assert(os.getenv('NAIVEPHYSICS_RESOLUTION'))),
   load_params = false,
   ticks_interval = 2,
   ticks_rate = 1/8,
   nticks = 100,
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


function M.get_check_occlusion_size(iteration)
   local size = 0
   local name = iteration.block
   if name:match('visible') or name:match('train') then
      size = 0
   elseif name:match('2$') then
      size = 2
   else
      size = 1
   end

   if name:match('C2') then
      size = size * 2
   end

   return size
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
   -- retrieve the current iteration in the table
   local iteration = assert(iterations_table[index])

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


-- Return the current iteration from 'iteration.t7' and the iteration table
function M.get_current_iteration()
   return M.get_iteration(current_index)
end


function M.prepare_next_iteration(was_valid)
   if was_valid and current_index == max_iteration then
      return 0
   end

   if was_valid then
      current_index = current_index + 1
   else
      local iteration = M.get_iteration(current_index)
      -- delete the saved data because the scene is not valid
      paths.rmall(iteration.path, 'yes')

      -- rerun the whole scene by coming back to its first iteration
      print('invalid scene, trying new parameters')
      if not M.is_train(iteration) then
         current_index = current_index - M.get_block_size(iteration) + iteration.type
      end
   end

   -- the number of remaining iterations
   local remaining = max_iteration - current_index + 1

   if remaining > 0 then
      -- ensure the iteration exists in the iterations table
      assert(iterations_table[current_index])
   end

   return remaining
end


-- Add a new iteration in the iterations table
local function add_iteration(b, t, i, n)
   local iteration = {block = b, type = t, id = i}
   if n then
      iteration.nactors = n
   end

   table.insert(iterations_table, iteration)
end


local train_runs, test_runs = 0, 0
local function add_train_iteration(block, case, nruns)
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


local function add_test_iterations(block, case, subblocks)
   for subblock, nruns in pairs(subblocks) do
      local name = block .. '.' .. case .. '_' .. subblock
      local ntypes = 4 + M.get_check_occlusion_size({block = name})


      if type(nruns) == 'table' then
         for nactors, nruns_2 in pairs(nruns) do
            for i = 1, nruns_2 do
               test_runs = test_runs + 1
               for t = ntypes, 1, -1 do
                  add_iteration(name, t, test_runs, tonumber(nactors))
               end
            end
            max_iteration = (max_iteration or 0) + ntypes * nruns_2
         end
      else -- nruns is an integer -> random nactors in each scene
         for i = 1, nruns do
            test_runs = test_runs + 1
            for t = ntypes, 1, -1 do
               add_iteration(name, t, test_runs)
            end
         end
         max_iteration = (max_iteration or 0) + ntypes * nruns
      end
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
function M.parse_config_file()
   local blocks = utils.read_json(conf.config_file)

   -- clean the global iterations table
   iterations_table = {}
   max_iteration = 0
   current_index = 1

   -- count the number of iterations both for train and test. Each
   -- train is always a single iteration, the number of test
   -- iterations is 4 + number of occlusion checks (depends on the
   -- block type)
   for block, cases in pairs(blocks) do
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
end


return M
