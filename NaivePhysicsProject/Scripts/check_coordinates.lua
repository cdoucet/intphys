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

-- A table filled with actor coordinates during ticking
local current_data

-- A table of coordinates loaded from the previous iteration (if
-- first_check is false)
local previous_data

-- The size of previous_data
local previous_data_size

-- A tick counter to compare current and previous coordinates in the tables
local index

-- True is all coordinates are equal up to the current iteration and
-- the current frame, false otherwise
local is_valid = true



-- Return a table with the current coordinates of an actor
--
-- The returned table has the following structure:
--   {x, y, z, pitch, yaw, roll}
local function get_actor_coordinates(actor)
   local l = uetorch.GetActorLocation(actor)
   local r = uetorch.GetActorRotation(actor)

   return {x = l.x, y = l.y, z = l.z,
           pitch = r.pitch, yaw = r.yaw, roll = r.roll}
end


-- Return true if |x - y| < epsilon, false otherwise
--
-- `x` and `y` must be tables with the following structure:
--   {x, y, z, pitch, yaw, roll}
-- `epsilon` default to 1e-6 if not specified
local function is_close_coordinates(x, y, epsilon)
   epsilon = epsilon or 1e-6

   return math.abs(x.x - y.x) < epsilon
      and math.abs(x.y - y.y) < epsilon
      and math.abs(x.z - y.z) < epsilon
      and math.abs(x.pitch - y.pitch) < epsilon
      and math.abs(x.yaw - y.yaw) < epsilon
      and math.abs(x.roll - y.roll) < epsilon
end


-- Register the actor current coordinates to the a table
local function push_current_coordinates()
   table.insert(current_data, get_actor_coordinates(actor))
end


-- Save the current coordinates to a file for the next iteration lookup
local function save_current_coordinates()
   if is_valid then
      torch.save(
         iteration.path .. '../check_' .. iteration.type .. '.t7',
         current_data)
   end
end


-- Compare current and previous coordinates for the current frame
--
-- Terminates the scene and set is_valid to false if a difference is
-- found
local function check_coordinates()
   if index <= previous_data_size
      and not is_close_coordinates(current_data[index], previous_data[index])
   then
      tick.set_ticks_remaining(0)
      is_valid = false

      print('bad actor coordinates')
   end

   index = index + 1
end


local M = {}


-- Initialize the check for a given iteration and a given actor
function M.initialize(_iteration, _actor)
   actor = _actor
   iteration = _iteration

   current_data = {}
   index = 1

   tick.add_hook(push_current_coordinates, 'slow')
   tick.add_hook(save_current_coordinates, 'final')

   -- True if the iteration is the first in the block (in that case we do
   -- not have a previous_data to load)
   local is_first_check = config.is_first_iteration_of_block(iteration)
   if not is_first_check then
      -- the previous iteration is n+1, as we execute them from n to 1
      previous_data = torch.load(iteration.path .. '../check_' .. iteration.type + 1 .. '.t7')
      previous_data_size = #previous_data
      tick.add_hook(check_coordinates, 'slow')
   end
end


-- Return true is the actor has homogoneous coordinates across iterations
function M.is_valid()
   return is_valid
end


return M
