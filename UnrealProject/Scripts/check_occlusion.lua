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

local M = {}

local data
local iteration
local actor
local is_check_occlusion


-- Return true if the `actor` is occluded in the rendered image
local function is_occluded(actor)
   return torch.max(uetorch.ObjectSegmentation({actor})) == 0
end


function M.initialize(_iteration, _actor, check_iterations)
   iteration = _iteration
   actor = _actor
   data = {}

   is_check_occlusion = false
   for _, v in ipairs(check_iterations) do
      if tostring(v) == tostring(iteration.type) then
         is_check_occlusion = true
         data[v] = {}
      end
   end

   if not is_check_occlusion then
      for _, v in ipairs(check_iterations) do
         data[v] = assert(torch.load(iteration.path .. '../occlusion_' .. tostring(v) .. '.t7'))
      end
   end
end


function M.hook()
   if is_check_occlusion then
      table.insert(data[iteration.type], is_occluded(actor))
   end
end


function M.end_hook()
   if not is_check_occlusion then
      return true
   end

   local check = false
   for _, v in ipairs(data[iteration.type]) do
      if v then
         check = true
         break
      end
   end

   if check then
      torch.save(
         iteration.path .. '../occlusion_' .. tostring(iteration.type) .. '.t7',
         data[iteration.type])
   end

   -- print('check occlusion: ' .. tostring(check))
   return check
end


function M.data(key, idx)
   return data[tonumber(key)][idx]
end


return M
