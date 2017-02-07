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
local tick = require 'tick'

local M = {}

local data
local iteration
local actor
local is_check_occlusion
local is_occlusion_started = false
local  is_occlusion_finished = false

-- Return true if the `actor` is occluded in the rendered image
local function is_occluded(actor)
   return torch.max(uetorch.ObjectSegmentation({actor})) == 0
end


local function middle(t)
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


function M.initialize(_iteration, _actor, check_iterations)
   iteration = _iteration
   actor = _actor
   data = {}

   is_check_occlusion = false
   for _, v in ipairs(check_iterations) do
      if tostring(v) == tostring(iteration.type) then
         is_check_occlusion = true
         data[v] = {raw = {}, middle = nil}
      end
   end

   if not is_check_occlusion then
      for _, v in ipairs(check_iterations) do
         data[v] = assert(torch.load(iteration.path .. '../occlusion_' .. tostring(v) .. '.t7'))
      end
   end
end


function M.tick()
   if is_check_occlusion and not is_occlusion_finished then
      local occluded = is_occluded(actor)
      if occluded and not is_occlusion_started then
         is_occlusion_started = true
      end

      if not occluded and is_occlusion_started and not is_occlusion_finished then
         is_occlusion_finished = true
         data[iteration.type].middle = middle(data[iteration.type].raw)
         tick.set_ticks_remaining(0)
      else
         table.insert(data[iteration.type].raw, occluded)
      end
   end
end


function M.final_tick()
   if not is_check_occlusion then
      return true
   end

   if is_occlusion_finished then
      torch.save(
         iteration.path .. '../occlusion_' .. tostring(iteration.type) .. '.t7',
         data[iteration.type])
      return true
   else
      return false
   end
end


function M.is_middle_of_occlusion(key, idx)
   return idx == data[tonumber(key)].middle
end


return M
