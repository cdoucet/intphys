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


-- Thid module is used for checking correct occlusions for the
-- occluded tests. Given a scene already parametrized, it ensures the
-- main actor is fully occluded during the scene. It also estimates
-- the tick corresponding to the middle of the occlusion, this tick
-- being used in the next iterations of the test to do the 'magic
-- trick' (the main actor must disappears or appears while it is fully
-- occluded).


local uetorch = require 'uetorch'
local tick = require 'tick'


local M = {}


-- The current iteration being executed
local iteration

-- The main actor on which we do the occlusion check
local actor

-- A table of ticks indexed booleans (false = main actor visible, true
-- = main actor occluded)
local data = {}

-- The tick numbers corresponding to middle of the occlusions
local middles = {}

-- True or false we perform an occlusion check on the current iteration
local is_check_occlusion

-- Flags to detect the begin and end of an occlusion
local is_occlusion_started, is_occlusion_finished = false, false


-- Return true if the `actor` is occluded in the rendered image
--
-- This function compute a mask on the main actor only (all other
-- actors being ignored). The actor is considered as occluded if the
-- whole mask is black.
local function is_occluded(actor)
   return torch.max(uetorch.ObjectSegmentation({actor})) == 0
end


-- Return the tick which is the middle of an occlusion
--
-- The table `t` must be a table of booleans with false = visible and
-- true = occluded. The function returns the mean index of the first
-- 'true' subtable encountered in `t`.
local function middle_of_occlusion(t)
   local first, last
   for k, v in ipairs(t) do
      if v and not first then
         first = k
      elseif not v and first and not last then
         last = k
         break
      end
   end
   last = last or #t

   assert(first and last)
   return math.floor((first + last) / 2)
end


-- Initialize the occlusion checker for the current iteration.
--
-- `actor` is the main actor on which the occlusion check is performed
-- `check_iterations` is a table of iteration types for which checks
-- are performed, e.g. {5} for blockC1_test_occluded_dynamic_1 or {6, 5}
-- for blockC1_test_occluded_dynamic_2
function M.initialize(_iteration, _actor, check_iterations)
   iteration = _iteration
   actor = _actor

   is_check_occlusion = false
   for _, v in ipairs(check_iterations) do
      if tostring(v) == tostring(iteration.type) then
         is_check_occlusion = true
      end
   end

   if is_check_occlusion then
      tick.add_hook(M.tick, 'slow')
      tick.add_hook(M.final_tick, 'final')
   else
      for _, v in ipairs(check_iterations) do
         local file = iteration.path .. '../occlusion_' .. tostring(v) .. '.t7'
         middles[v] = torch.load(file)
      end
   end
end


-- Check for occlusion start and stop in the current scene. Stop
-- rendering when a complete occlusion has been found.
function M.tick()
   local occluded = is_occluded(actor)
   if occluded and not is_occlusion_started then
      is_occlusion_started = true
   end

   if not occluded and is_occlusion_started then
      middles[iteration.type] = middle_of_occlusion(data)
      is_occlusion_finished = true
      tick.set_ticks_remaining(0)
   else
      table.insert(data, occluded)
   end
end


-- If the current iteration is an occlusion check, returns true if a
-- complete occlusion has been found in the scene, false otherwise, it
-- also save the middle tick to a file. If the iteration is not an
-- iteration check, it returns true.
function M.final_tick()
   if is_occlusion_finished then
      torch.save(
         iteration.path .. '../occlusion_' .. tostring(iteration.type) .. '.t7',
         middles[iteration.type])
   end
end


function M.is_valid()
   if not is_check_occlusion or is_occlusion_finished then
      return true
   else
      print('occlusion not valid')
      return false
   end
end


-- Return true if the `tick` corresponds to the middle of an occlusion
-- for the iteration type specified, false otherwise.
function M.is_middle_of_occlusion(iteration_type, tick)
   return tick == middles[tonumber(iteration_type)]
end


return M
