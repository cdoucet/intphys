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


-- This module handles game loop ticks. It provides 3 ticking levels
-- at which some functions can be registered:
--   * the 'fast' level ticks at each game tick,
--   * the 'slow' level ticks each few game loop as defined by
--     config.get_tick_interval(),
--   * the 'final' level ticks only once, at the very end of the scene
--     rendering.
--
-- A function f is registered to tick at a given level l using the
-- function tick.add_hook(f, l), l being 'slow', 'fast' or 'final'.

local uetorch = require 'uetorch'


local M = {}


-- Tables registering hooks for the different ticking levels
local hooks = {slow = {}, fast = {}, final = {}}


-- Number of ticks to execute before calling the final hooks
local nticks

-- Interval between two game ticks in which the slow hooks are called
local ticks_interval

-- -- two variables to compute the ticks interval
local t_tick, t_last_tick = 0, 0

-- A tick counter, from 0 to nticks
local ticks_counter


-- Set a constant tick rate and register ticking in uetorch
function M.initialize(_nticks, _ticks_interval, ticks_rate)
   nticks = _nticks
   ticks_interval = _ticks_interval
   ticks_counter = 0

   -- set a constant ticking rate
   ticks_rate = ticks_rate or 1/8
   uetorch.SetTickDeltaBounds(ticks_rate, ticks_rate)

   -- replace the uetorch's default tick function by our own
   Tick = M.tick
end


-- Set the number of slow ticks before the end of the scene
function M.set_ticks_remaining(ticks_remaining)
   ticks_counter = nticks - ticks_remaining + 1
end


-- Return the number of slow ticks since the beginning of the scene
function M.get_counter()
   return ticks_counter
end


-- Register a hook function `f` called at a given ticking level
--
-- The function `f` should take a single argument and return nil
-- The level must be 'slow', 'fast', or 'final'
function M.add_hook(f, level)
   table.insert(hooks[level], f)
end


-- Unregister the function `f` from the given level hooks
--
-- The level must be 'slow', 'fast', or 'final'
function M.remove_hook(f, level)
   local t = hooks[level]
   for i = #t, 1, -1 do
      if t[i] == f then
         table.remove(t, i)
      end
   end
end


-- Clear all the registered hooks
function M.clear()
   for _, hook in pairs(hooks) do
      hook = {}
   end
end

-- Run all the registerd at a given ticking level
--
-- The level must be 'slow', 'fast', or 'final'
function M.run_hooks(level, ...)
   for _, f in ipairs(hooks[level]) do
      f(...)
   end
end


-- This function must be called at each game loop by UETorch
--
-- It increment the tick counter, calling each registerd hook until
-- the end of the scene.
function M.tick(dt)
   -- dt not used here is the time since the last tick
   if ticks_counter then
      if ticks_counter < nticks then
         M.run_hooks('fast')

         if t_tick - t_last_tick >= ticks_interval then
            t_last_tick = t_tick

            ticks_counter = ticks_counter + 1
            M.run_hooks('slow')
         end
         t_tick = t_tick + 1
      else
         M.run_hooks('final')
         ticks_counter = nil
      end
   end
end


return M
