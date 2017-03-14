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


-- This module defines some various utility functions

local uetorch = require 'uetorch'
local json = require 'dkjson'


local M = {}


-- Return true if `name` is a readable file, false otherwise
function M.file_exists(name)
   local f=io.open(name,"r")
   if f~=nil then io.close(f) return true else return false end
end


-- Return the sign of the number `x` as -1, 0 or 1
function M.sign(x)
   if x<0 then
      return -1
   elseif x>0 then
      return 1
   else
      return 0
   end
end


-- Return the sum of values in the table t
function M.sum(t)
   local s = 0
   for _, v in pairs(t) do
      s = s + v
   end
   return s
end


-- Return unique elements of a tensor `t` in a table
--
-- Equivalent to set(t) in Python. From
-- https://stackoverflow.com/questions/20066835
function M.unique(t)
   local hash, res = {}, {}
   t:apply(
      function(x) if not hash[x] then res[#res+1] = x; hash[x] = true end end)
   return res
end


-- Pad a number `int` with `n` beginning zeros, return it as a string
--
-- pad_zeros(0, 3)  -> '000'
-- pad_zeros(12, 3) -> '012'
-- pad_zeros(12, 1) -> '12'
function M.pad_zeros(int, n)
   s = tostring(int)
   for _ = 1, n - #s do
      s = '0' .. s
   end
   return s
end


-- Load a JSon file as a table
function M.read_json(file)
   local f = assert(io.open(file, "rb"))
   local content = f:read("*all")
   f:close()
   return json.decode(content)
end


-- Write a table as a JSon file
--
-- `keyorder` is an optional array to specify the ordering of keys in
-- the encoded output. If an object has keys which are not in this
-- array they are written after the sorted keys.
function M.write_json(t, file, keyorder)
   local f = assert(io.open(file, "wb"))
   if keyorder then
      f:write(json.encode(t, {indent = true, level = 1, keyorder = keyorder}))
   else
      f:write(json.encode(t, {indent = true, level = 1}))
   end
   f:close()
end


function M.location(x, y, z)
   return {x = x, y = y, z = z}
end

function M.rotation(pitch, yaw, roll)
   return {pitch = pitch, yaw = yaw, roll = roll}
end

M.scale = M.location

-- Return the `actor` rotation vector as a string
function M.rotation_to_string(actor)
   local r = uetorch.GetActorRotation(actor)
   return r.pitch .. ' ' .. r.yaw .. ' ' .. r.roll
end


-- Return the `actor` location vector as a string
function M.location_to_string(actor)
   local l = uetorch.GetActorLocation(actor)
   return l.x .. ' ' .. l.y .. ' ' .. l.z
end

-- Return the location and rotation of an actor in a string
--
-- The returned string is formatted as:
--   'x y z pitch yaw roll'
function M.coordinates_to_string(actor)
   return M.location_to_string(actor) .. ' ' .. M.rotation_to_string(actor)
end


return M
