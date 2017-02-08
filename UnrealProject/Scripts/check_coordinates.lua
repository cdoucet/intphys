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
-- impossibles). Basically it stores the actor coordinates during
-- ticking and, in the final tick, compare thoses coordinates to the
-- coordinates of the previous run. If those coordinates are not
-- equal, the check fails.


local uetorch = require 'uetorch'
local config = require 'config'
local utils = require 'utils'


local M = {}

-- The current iteration
local iteration

-- The scene actor on which to operate the check
local actor

-- A table fiiled with actor coordinates during ticking
local data = {}

-- A flag, true if we run the check for the current iteration, false
-- otherwise
local is_check = false


-- Initialize the check for a given iteration and a given actor
function M.initialize(_iteration, _actor)
   actor = _actor
   iteration = _iteration
   if not config.is_check_occlusion(iteration) then
      is_check = true
   end
end


-- Register actor coordinates in a table
function M.tick()
   if is_check then
      table.insert(data, utils.get_actor_coordinates(actor))
   end
end


-- Save the coordinates to a file and compare them to previous
-- cooridinates (if any)
function M.final_tick()
   local check = true
   if is_check and not config.is_first_iteration_of_block(iteration, false) then
      local nticks = config.get_nticks()

      -- compare the actual data to the previous one
      last_data = torch.load(iteration.path .. '../check_' .. iteration.type + 1 .. '.t7')
      for i = 1, nticks do
         if not utils.is_close_coordinates(data[i], last_data[i]) then
            check = false
            break
         end
      end
   end

   if check then
      torch.save(iteration.path .. '../check_' .. iteration.type .. '.t7', data)
   end

   return check
end


return M
