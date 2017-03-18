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


-- This module defines the background wall behavior. Random texture,
-- height, width and distance from the camera. The background wall is
-- a U-shaped wall surrounding the scene. It has physics enabled so
-- the spheres can collide to it.

local uetorch = require 'uetorch'
local material = require 'material'

local actor


local M = {}


-- Generate a random set of attributes for the background wall
--
-- Params:
--    is_active (bool): if true, the backwall is active in the scene,
--       if false the backwall is disabled and the method returns nil.
--
--    If is_active is omitted, it is set to true or false with a 50%
--    probability (the wall is randomly absent or present).
--
-- Returns:
--    If the backwall is active, the returned table has the following
--    entries:
--       {material, height, depth, width}
--    Else it returns an empty table
function M.get_random_parameters(is_active)
   local params = {}

   is_active = is_active or (math.random() < 0.5)
   if is_active then
      params.xwidth = math.random() * 2500 + 1500
      params.ylocation = math.random() * 600 - 1500
      params.zscale = math.random() * 9 + 1
      params.material = material.random('wall')
   end

   return params
end


-- Initialize a background wall with a spawned actor
function M.initialize(actor_name)
   if not actor_name then
      actor = nil
   else
      actor = uetorch.GetActor(actor_name)
   end
end


function M.is_active()
   return actor ~= nil
end


-- return the backwall, or nil if not active
function M.get_actor()
   return actor
end


function M.get_nactors()
   if M.is_active() then
      return 1
   else
      return 0
   end
end


return M
