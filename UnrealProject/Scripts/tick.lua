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


-- This module contains functions for handling game loop
-- ticks. Registering of function to be called at each tick and at the
-- final tick.

local uetorch = require 'uetorch'

local M = {}


-- A table registering ticks hooks
local tick_hooks = {}

-- A table registering final tick hooks
local end_tick_hooks = {}

-- Remaining ticks before the final one
local ticks_remaining = nil


-- Fix the tick rate of the game at a constant rate (in s.)
function M.set_tick_delta(dt)
   uetorch.SetTickDeltaBounds(1/8, 1/8)
end


-- Set the number of ticks before the end of the scene
function M.set_ticks_remaining(ticks)
   ticks_remaining = ticks
end


-- Register a hook function f called at each game loop tick
--
-- Tick hooks should take a single argument (dt) and return nil
function M.add_tick_hook(f)
   table.insert(tick_hooks, f)
end


-- Register a hook function f called at the end of each scene
--
-- Tick hooks should take a single argument (dt) and return nil
function M.add_end_tick_hook(f)
   table.insert(end_tick_hooks, f)
end


-- Remove the function f from the ticks hooks register
function M.remove_tick_hook(f)
   for i = #tick_hooks, 1, -1 do
      if tick_hooks[i] == f then
         table.remove(tick_hooks, i)
      end
   end
end


-- This function must be called at each game loop by UETorch
--
-- It increment the tick counter, calling each registerd hook, until
-- the end of the scene where it calls ending hooks
function M.tick(dt)
   dt = 1

   if ticks_remaining then
      ticks_remaining = ticks_remaining - dt
      -- print('remaining ' .. ticks_remaining)

      if ticks_remaining < 0 then
         -- end of the scene, run end hooks and go to the next iteration
         ticks_remaining = nil
         for _, hook in ipairs(end_tick_hooks) do
            hook()
         end
         uetorch.ExecuteConsoleCommand("RestartLevel")
      else
         -- the scene is running, run tick hooks
         for _, hook in ipairs(tick_hooks) do
            hook(dt)
         end
      end
   end
end


return M
