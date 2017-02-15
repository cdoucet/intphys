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
-- of the scene has the same coordinates (location and rotation)
-- during all the test variations (possibles and
-- impossibles). Basically it compares the coordinates from the
-- current iteration to the previous one of the same block, and store
-- the current coordinates for the next iteration's check.


local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'
local tick = require 'tick'


local M = {}

-- The current iteration
local iteration

-- The scene actor on which to operate the check
local actor

-- A flag, true if we run the check for the current iteration, false
-- otherwise
local is_check

-- A counter to get the coordinates of the curretn tick
local index

-- A flag, true if the iteration is the first on ein the block (in
-- that case we do not have a previous_data to load)
local is_first_check

-- A table filled with actor coordinates during ticking
local current_data

-- A table of coordinates loaded from the previous iteration (if the
-- current iteration is not the first one in the current block)
local previous_data


local is_valid = true


-- Initialize the check for a given iteration and a given actor
function M.initialize(_iteration, _actor)
   actor = _actor
   iteration = _iteration

   if not config.is_check_occlusion(iteration) then
      is_check = true
      is_first_check = config.is_first_iteration_of_block(iteration, false)
      current_data = {}
      index = 1

      tick.add_hook(M.push_data, 'slow')

      if not is_first_check then
         previous_data = torch.load(iteration.path .. '../check_' .. iteration.type + 1 .. '.t7')
         tick.add_hook(M.check_data, 'slow')
      end

      tick.add_hook(M.final_tick, 'final')
   end
end


-- Register the current actor coordinates in a table
function M.push_data()
   table.insert(current_data, utils.get_actor_coordinates(actor))
end


-- Compare current and previous coordinates, terminates the scene if a
-- difference is found
function M.check_data()
   if not utils.is_close_coordinates(current_data[index], previous_data[index]) then
      is_valid = false
      print('actor coordinates do not match')
      tick.set_ticks_remaining(0)
   end

   index = index + 1
end


-- Save the current coordinates to a file for the next iteration
function M.final_tick()
   if is_valid then
      torch.save(
         iteration.path .. '../check_' .. iteration.type .. '.t7',
         current_data)
   end
end


-- return true is the scene had correct coordinates
function M.is_valid()
   return is_valid
end

return M
