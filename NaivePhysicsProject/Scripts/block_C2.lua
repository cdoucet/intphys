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
local utils = require 'utils'
local tick = require 'tick'
local occluders = require 'occluders'
local actors = require 'actors'
local check_occlusion = require 'check_occlusion'


local subblocks = {
   'train',
   -- 'test_visible_static',
   -- 'test_visible_dynamic_1',
   -- 'test_visible_dynamic_2',
   -- 'test_occluded_static',
   -- 'test_occluded_dynamic_1',
   -- 'test_occluded_dynamic_2'
}


local subblock

local iteration

local params

local main_actor

local is_possible

local is_visible_start

local trick


local function is_valid_subblock(name)
   for _, subblock in ipairs(subblocks) do
      if name == subblock then
         return true
      end
   end
   return false
end



local M = {}


function M.get_main_actor()
   return main_actor
end


function M.is_possible()
   return is_possible
end


-- Return random parameters the the given subblock
function M.get_random_parameters(subblock)
   assert(is_valid_subblock(subblock))

   local t_shapes = {'sphere', 'cube', 'cylinder'}
   local t_actors = {}
   for i = 1, math.random(1, 3) do
      local s = t_shapes[math.random(1, #t_shapes)]
      if t_actors[s] then
         t_actors[s] = t_actors[s] + 1
      else
         t_actors[s] = 1
      end
   end

   if subblock:match('train') then
      return {
         occluders = occluders.random(),
         actors = actors.get_random_parameters(t_actors)}
   end
end


function M.initialize(_subblock, _iteration, _params)
   subblock = _subblock
   iteration = _iteration
   params = _params

   if iteration.type == 1 then
      is_visible_start = false
      is_possible = true
   elseif iteration.type == 2 then
      is_visible_start = true
      is_possible = true
   elseif iteration.type == 3 then
      is_visible_start = false
      is_possible = false
   elseif iteration.type == 4 then
      is_visible_start = true
      is_possible = false
   else -- this includes iterations for train and occlusion checks
      is_visible_start = true
      is_possible = true
   end
end


function M.get_occlusion_check_iterations(s)
   s = s or subblock
   if s:match('train') or s:match('visible') then
      return {}
   else
      local it = {}
      local idx = 1
      if s:match('_2$') then idx = 2 end
      for i = idx, 1, -1 do
         table.insert(it, 4 + i)
      end
      return it
   end
end


return M
