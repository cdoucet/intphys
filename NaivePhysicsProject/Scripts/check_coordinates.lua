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
-- of the scene has the same coordinates (location and rotation
-- vectors) frame per frame in the whole test quadruplet.
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

-- The scene actor on which to operate the check
local actor

-- A tensor filled with actor coordinates of the current iteration
local current_data

-- A tensor filled with actor coordinates of the previous iteration
local previous_data

-- True is all coordinates are equal up to the current iteration and
-- the current frame, false otherwise
local is_valid


-- Return a tensor with the current location of an actor
local function get_actor_coordinates(actor)
   local l = assert(uetorch.GetActorLocation(actor))
   return torch.Tensor({l.x, l.y, l.z})
end


-- Register the actor current coordinates to the a table
local function push_current_coordinates()
   current_data[tick.get_counter()] = get_actor_coordinates(actor)
end


-- Save the current coordinates to a tensor for the next iteration lookup
local function save_current_coordinates()
   if is_valid then
      local c = current_data
      local n = tick.get_counter()
      previous_data = torch.Tensor(c:size()):copy(c):narrow(1, 1, n)
   end
end


-- Compare current and previous coordinates for the current frame
--
-- Terminates the scene and set is_valid to false if a difference is
-- found
local function check_coordinates()
   local index = tick.get_counter()
   if index <= previous_data:size(1) then
      -- euclidean distance of current/previous location
      local dist = math.sqrt((current_data[index] - previous_data[index]):pow(2):sum())
      if dist > 10e-6 then
         tick.set_ticks_remaining(0)
         is_valid = false
         print('bad actor coordinates (tick ' .. tick.get_counter() .. '): ' .. dist)
         torch.save(
            'coords.t7',
            {current = current_data:narrow(1, 1, index), previous = previous_data})
         uetorch.ExecuteConsoleCommand('Exit')
         return
      end
   end
end


local M = {}


-- Initialize the check for a given iteration and a given actor
function M.initialize(_iteration, _actor)
   actor = _actor
   iteration = _iteration
   is_valid = true

   current_data = torch.Tensor(config.get_nticks(), 3):fill(0)

   tick.add_hook(push_current_coordinates, 'slow')
   tick.add_hook(save_current_coordinates, 'final')
   if not config.is_first_iteration_of_block(iteration) then
      tick.add_hook(check_coordinates, 'slow')
   end
end


-- Return true is the actor has homogoneous coordinates across iterations
function M.is_valid()
   if is_valid == nil then
      return true
   else
      return is_valid
   end
end


function M.change_actor(_actor)
   actor = _actor
end


return M
