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
local material = require 'material'
local check_occlusion = require 'check_occlusion'


local subblocks = {
   'test_visible_static_2',
   'test_visible_dynamic_2',
   'test_occluded_static_2',
   'test_occluded_dynamic_2'
}


local subblock

local iteration

local params

local main_object

local is_possible

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


function M.get_main_object()
   return main_object
end


function M.is_possible()
   return is_possible
end


function M.get_random_parameters(subblock, nobjects)
   assert(is_valid_subblock(subblock))
   nobjects = nobjects or math.random(1, 3)

   local params = {}

   return params
end


function M.initialize(_subblock, _iteration, _params)
   subblock = assert(_subblock)
   iteration = assert(_iteration)
   params = assert(_params)

   main_object = nil
   trick = nil

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
   else  -- this includes iterations for train and occlusion checks
      is_visible_start = true
      is_possible = true
   end

   -- on train iteration we have no more job
   if iteration.type == -1 then return end
end
