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
--   * the 'normal' level ticks each few game loop as defined by
--     config.get_tick_interval(),
--   * and the 'final' level ticks only once, at the very end of the scene
--     rendering, just before exit.
--
-- A function f is registered to tick at a given level l using the
-- function tick.add_hook(f, l), l being 'slow', 'fast' or 'final'.

local uetorch = require 'uetorch'
local config = require 'config'

local M = {}


-- Tables registering hooks for the different ticking levels
local hooks = {slow = {}, fast = {}, final = {}}

-- Remaining ticks before the final one
local ticks_remaining = config.get_nticks()

local step = 0

-- Interval between two game ticks in which the hooks are called, and
-- two variables to compute it
local ticks_interval, t_tick, t_last_tick = config.get_ticks_interval(), 0, 0


-- Fix the tick rate of the game at a constant rate
function M.set_tick_delta(dt)
   uetorch.SetTickDeltaBounds(dt, dt)
end


-- -- Set the number of ticks before the end of the scene
-- function M.set_ticks_remaining(ticks)
--    ticks_remaining = ticks
-- end


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
   local t = hook[level]
   for i = #t, 1, -1 do
      if t[i] == f then
         table.remove(t, i)
      end
   end
end


-- Run all the registerd at a given ticking level
--
-- The level must be 'slow', 'fast', or 'final'
function M.run_hooks(level, ...)
   for _, f in pairs(hooks[level]) do
      f(...)
   end
end


-- This function must be called at each game loop by UETorch
--
-- It increment the tick counter, calling each registerd hook until
-- the end of the scene.
function M.tick(dt)
   dt = 1

   if ticks_remaining >= 0 then
      -- the scene is running, run tick hooks
      M.run_hooks('fast', dt)

      if t_tick - t_last_tick >= ticks_interval then
         ticks_remaining = ticks_remaining - 1
         step = step + 1

         M.run_hooks('slow', step)

         t_last_tick = t_tick
      end
      t_tick = t_tick + 1
   else
      -- end of the scene, run end hooks and go to the next iteration
      M.run_hooks('final')
      uetorch.ExecuteConsoleCommand('RestartLevel')
   end
end


return M
