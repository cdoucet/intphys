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


-- This module defines the occluders behavior.
--
-- Generation of random parameters, setup of up to 2 occluders, a tick
-- method handling the occluders movements.

local uetorch = require 'uetorch'
local material = require 'material'
local utils = require 'utils'
local tick = require 'tick'


-- Registers the active occluders, mobile or not, and their number
local active_occluders, noccluders
local normalized_names

local M = {}


function M.get_random_parameters(noccluders, subblock)
   noccluders = noccluders or math.random(0, 2)
   subblock = subblock or 'train'

   local params = {}

   for i = 1, noccluders do
      local name = 'occluder_' .. tostring(i)
      params[name] = M.get_random_occluder_parameters(name, subblock)
   end

   if not next(params) then
      return nil
   else
      return params
   end
end


-- Initialize the occluders with given names
function M.initialize(actors_name)
   active_occluders = {}
   normalized_names = {}
   noccluders = 0

   for idx, name in ipairs(actors_name) do
      local actor = uetorch.GetActor(name)
      active_occluders[name] = actor

      local n = name:gsub('C_.*$', ''):gsub('^%u', string.lower) .. idx
      normalized_names[n] = actor

      noccluders = noccluders + 1
   end
end


-- destroy a spawned occluder given its name
function M.destroy_by_order(idx)
   local s2n = function(s) return tonumber(s:gsub('^.*_', '')) end
   local name = utils.get_index_in_sorted_table(
      M.get_occluders(), idx, function(a,b) return s2n(a) < s2n(b) end)

   uetorch.DestroyActor(active_occluders[name])
   active_occluders[name] = nil
   noccluders = noccluders - 1
end


-- Return the table (name -> actor) of the active occluders
--
-- Active occluders are those initialized from parameters
function M.get_occluders()
   return active_occluders or {}
end


function M.get_occluders_normalized_names()
   return normalized_names or {}
end

-- Return the number of active occluders
function M.get_noccluders()
   return noccluders or 0
end


function M.get_random_occluder_parameters(name, subblock)
   -- index of the occluder we are generating parameters for
   local idx = name:gsub('occluder_', '')
   idx = tonumber(idx)

   local params = {}
   params.material = material.random('wall')

   -- for train, occluders are fully random
   if subblock:match('train') then
      local shift = {0, 500}
      params.location = {x = shift[idx] - 300, y = -150 - shift[idx], z = 20}

      -- Rotation around the Z axis in degree
      params.rotation = math.random(-90, 90)

      params.scale = {x = math.random() + 0.5, y = 1, z = 1.5 - 0.3 * math.random()}

      -- Start position is randomly 'up' or 'down'
      params.start_position = (math.random(0, 1) == 1 and 'up' or 'down')

      -- Select random motion steps for the occluder (0 -> no motion,
      -- 0.5 -> single one way, 1 -> one round trip, 1.5 -> one round
      -- trip and a half, 2 -> two round trips)
      params.movement = math.random(0, 4) / 2

      params.rotation_speed = math.random()*20 + 5

      -- a brief pause between each movement steps
      params.pause = {}
      for i=1, params.movement*2 do
         table.insert(params.pause, math.random() * 2)
      end

      return params
   end

   -- we are generating occluders for test iterations, with a more
   -- controlled variability
   params.rotation_speed = 100
   params.movement = 1
   params.rotation = 0
   params.start_position = 'down'
   params.pause = {math.random(10), math.random(10)}
   params.scale = {x = 0.6 - 0.2 * math.random(), y = 1, z = 1.0 - 0.4 * math.random()}
   --params.scale = {x = 0.5, y = 1, z = 1 - 0.4 * math.random()}

   -- occluder's location depends on subblock
   if subblock:match('dynamic_2') then
      local x = {-100, 200}
      params.location = {x = x[idx], y = -350, z = 20}
   elseif subblock:match('dynamic_1') then
      params.location = {x = 50, y = -350, z = 20}
   else
      assert(subblock:match('static'))
      params.pause = {5 + math.random(20), math.random(20)}
      params.location = {x = 100 - 200 * params.scale.x, y = -350, z = 20}
   end

   return params
end


return M
