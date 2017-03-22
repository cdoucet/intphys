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


-- This module is used during test iterations to ensure the main actor
-- of the scene has the same frame per frame coordinates in the whole
-- test quadruplet.
--
-- Basically it compares the coordinates of a choosen actor from the
-- current iteration to the previous one (the first one excepted),
-- storing the current coordinates for the next iteration lookup.
--
-- When different coordinates are detected for the same frame in two
-- successive iterations of a quadruplet, the scene terminates and is
-- invalidated.


local uetorch = require 'uetorch'
local config = require 'config'
local tick = require 'tick'


-- The current iteration
local iteration

-- A method to get back the scene actor on which to operate the check
local actor

-- A tensor filled with actor coordinates of the current iteration
local current_data

-- A table of tensors filled with actor coordinates on reference iterations
local reference_data

-- The index where to read reference data for the current iteration,
-- by default this is 1 as we need to store a single trajectory. But
-- for block O2 we store 2 trajectories, one for each mesh.
local reference_index = 1

-- True is all coordinates are equal up to the current iteration and
-- the current frame, false otherwise
local is_valid


-- Register the actor current coordinates to the a table
local function push_current_coordinates()
   local l = assert(uetorch.GetActorLocation(actor))
   current_data[tick.get_counter()] = torch.Tensor({l.x, l.y, l.z})
end


-- Save the current coordinates to a tensor for the next iteration lookup
local function save_current_coordinates()
   if is_valid then
      local n = tick.get_counter()
      local narrowed = current_data:narrow(1, 1, n)
      reference_data[reference_index] = torch.Tensor(narrowed:size()):copy(narrowed)
   end
end


-- Compare current and previous coordinates for the current frame
--
-- Terminates the scene and set is_valid to false if a difference is
-- found
local function push_and_check_coordinates()
   local index = tick.get_counter()
   push_current_coordinates()

   if reference_data[reference_index]
      and index <= reference_data[reference_index]:size(1)
   then
      -- euclidean distance of current/previous location
      local diff = current_data[index] - reference_data[idx][index]
      local dist = math.sqrt(diff:pow(2):sum())
      if dist > 10e-3 then
         tick.set_ticks_remaining(0)
         is_valid = false

         print('bad actor coordinates (tick ' .. tick.get_counter() ..
                  '): distance = ' .. dist .. ' cm')
         return
      end
   end
end


local M = {}


-- Initialize the check for a given iteration and a given actor
function M.initialize(_iteration, _actor)
   iteration = _iteration
   actor = _actor
   is_valid = true
   current_data = torch.Tensor(config.get_nticks(), 3):fill(0)
   reference_data = {}

   if config.is_first_iteration_of_block(iteration) then
      tick.add_hook(push_current_coordinates, 'slow')
   else
      tick.add_hook(push_and_check_coordinates, 'slow')
   end
   tick.add_hook(save_current_coordinates, 'final')
end


-- Return true is the actor has homogoneous coordinates across iterations
function M.is_valid()
   if is_valid == nil then
      return true
   else
      return is_valid
   end
end


function M.set_reference_index(idx)
   reference_index = idx
end


return M
