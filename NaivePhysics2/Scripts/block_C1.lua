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
   'train',
   'test_visible_static',
   'test_visible_dynamic_1',
   'test_visible_dynamic_2',
   'test_occluded_static',
   'test_occluded_dynamic_1',
   'test_occluded_dynamic_2'
}


local subblock

local iteration

local params

local main_object

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


function M.get_main_object()
   return main_object
end


function M.is_possible()
   return is_possible
end


-- Return random parameters the the given subblock
function M.get_random_parameters(subblock, nobjects)
   assert(is_valid_subblock(subblock))
   nobjects = nobjects or math.random(1, 3)

   local params = {}

   -- occluders
   if subblock:match('train') then
      params.occluders = occluders.get_random_parameters(math.random(0, 2))
   else
      local noccluders = #(M.get_occlusion_check_iterations(subblock))
      params.occluders = occluders.get_random_parameters(noccluders, subblock)
   end

   -- objects
   if subblock:match('train') then
      local t_objects, t_shapes = {}, {}
      for i = 1, nobjects do
         table.insert(t_objects, 'object_' .. i)
         table.insert(t_shapes, 'sphere')
      end
      params.objects = actors.get_random_parameters(t_objects, t_shapes)

   else  -- we are in a test subblock

      -- setup the objects parameters and the main object (on which
      -- the magic trick is applied)
      params.main_object = 'object_' .. math.random(1, nobjects)
      params.objects = {}

      for i = 1, nobjects do
         params.objects['object_' .. i] = {}
         local p = params.objects['object_' .. i]

         -- scale, mesh, material and rotation are the same across all
         -- subblocks
         local s = 0.7 + 0.5 * math.random()
         p.scale = {x = s, y = s, z = s}
         p.mesh = 'Sphere'
         p.material = material.random('actor')
         p.rotation = {pitch = 0, yaw = 0, roll = 0}

         -- location an dofrce varies across subblocks
         if subblock:match('static') then
            local x_loc = {150, 40, 260}
            p.location = {x = x_loc[i], y = -550, z = 70}
            p.location.z = 100 * p.scale.x / 2.0 + 20
            p.force = {x = 0, y = 0, z = 0}

         elseif subblock:match('dynamic_1') then
            p.location = {x = -400, y = -550 - 150 * (i - 1), z = 70 + math.random(200)}
            p.force = {
                  x = math.random(8e5, 1.1e6), y = 0,
                  z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

            if actors.random_side() == 'right' then
               p.location.x = 500
               p.force.x = -1 * p.force.x
            end
         else
            assert(subblock:match('dynamic_2'))

            p.side = actors.random_side()
            p.location = {x = -350, y = -550 - 150 * (i - 1), z = 70 + math.random(200)}
            p.force = {
               x = 1.6e6, y = 0,
               z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

            if p.side == 'right' then
               p.location.x = 750
               p.force.x = -1 * p.force.x
            end
         end
      end

      -- setup the trick parameters for the visible subblocks (for
      -- occluded blocks this is done by the check_occlusion module)
      if subblock:match('visible') then
         if subblock:match('static') then
            -- the step at which the magic trick is done
            params.trick_step = math.floor((0.3*math.random() + 0.2) * config.get_nticks())
         elseif subblock:match('dynamic_1') then
            -- the x position on which the magic trick is done
            params.trick_x = math.random()*250 + 50
         else  -- dynamic_2
            -- length and start position (on the x axis) of the magic
            -- disparition/apparition of a sphere
            local trick_length = math.random() * 250 + 200
            local main_object_side = assert(params.objects[params.main_object].side)
            if main_object_side == 'right' then
               params.trick_start = math.random() * (400 - trick_length) + trick_length
               params.trick_stop = params.trick_start - trick_length
            else
               params.trick_start = math.random() * (400 - trick_length)
               params.trick_stop = params.trick_start + trick_length
            end
         end
      end
   end

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
   if iteration.type == -1 then
      return
   end

   -- on test, setup the main actor.
   main_object = actors.get_active_actors_normalized_names()[params.main_object]
   uetorch.SetActorVisible(main_object, is_visible_start)

   if subblock:match('dynamic_2') then
      if iteration.type == 6 then occluders.destroy_normalized_name('occluder_1') end
      if iteration.type == 5 then occluders.destroy_normalized_name('occluder_2') end
   end

   -- when we are in an occlusion test, remove all the actors excepted
   -- the main one TODO better not to spaw them
   if iteration.type == 5 or iteration.type == 6 then
      for name, object in pairs(actors.get_active_actors()) do
         if object ~= main_object then
            actors.destroy_actor(name)
         end
      end
   end

   -- initialize the ticking method that do the magic stuff
   if not M.is_possible() then
      tick.add_hook(M.magic_trick, 'slow')

      -- setup the trick data
      if subblock:match('dynamic_2') then
         trick = {is_done_1 = false, is_done_2 = false}

         if subblock:match('occluded') then
            local first, second = 5, 6
            if (assert(params.objects[params.main_object].side) == 'right') then
               first, second = 6, 5
            end

            trick.can_do_1 = function() return check_occlusion.is_middle_of_occlusion(first) end
            trick.can_do_2 = function() return check_occlusion.is_middle_of_occlusion(second) end

         else  -- dynamic_2 visible
            trick.xdiff_start = nil
            trick.xdiff_stop = nil
            trick.xdiff = function(x)
               return utils.sign(uetorch.GetActorLocation(main_object).x - x)
            end
            trick.can_do_1 = function()
               if not trick.xdiff_start then
                  trick.xdiff_start = trick.xdiff(assert(params.trick_start))
                  trick.xdiff_stop = trick.xdiff(assert(params.trick_stop))
               end
               return trick.xdiff(params.trick_start) ~= trick.xdiff_start
            end
            trick.can_do_2 = function()
               return trick.xdiff(params.trick_stop) ~= trick.xdiff_stop
            end
         end
      else  -- dynamic_1 or static
         trick = {is_done = false}

         if subblock:match('occluded') then
            trick.can_do = function()
               return check_occlusion.is_middle_of_occlusion(5) end
         elseif subblock:match('static') then -- visible static
            trick.can_do = function()
               return tick.get_counter() == assert(params.trick_step) end
         else -- visible dynamic_1
            trick.init_xdiff = nil
            trick.xdiff = function()
               return utils.sign(params.trick_x - uetorch.GetActorLocation(main_object).x)
            end
            trick.can_do = function()
               if not trick.init_xdiff then
                  trick.init_xdiff = trick.xdiff()
               end
               return trick.xdiff() ~= trick.init_xdiff
            end
         end
      end
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


function M.is_main_object_active()
   local p = M.is_possible()
   local v = is_visible_start
   if p and v then
      return true
   elseif p and not v then
      return false
   end

   if subblock:match('dynamic_2') then
      local t1, t2 = trick.is_done_1, trick.is_done_2
      return (v and not t1 and not t2)
         or (not v and t1 and not t2)
         or (v and t1 and t2)
   else  -- this is static or dynamic_1
      local t = trick.is_done
      return (v and not t) or (not v and t)
   end
end


function M.magic_trick()
   if subblock:match('dynamic_2') then
      if not trick.is_done_1 and trick.can_do_1() then
         trick.is_done_1 = true
         uetorch.SetActorVisible(main_object, not is_visible_start)
      elseif trick.is_done_1 and not trick.is_done_2 and trick.can_do_2() then
         uetorch.SetActorVisible(main_object, is_visible_start)
         trick.is_done_2 = true
         -- assert(tick.remove_hook(M.magic_trick, 'slow'))
      end
   else  -- this is static or dynamic_1
      if not trick.is_done and trick.can_do() then
         uetorch.SetActorVisible(main_object, not is_visible_start)
         trick.is_done = true
         -- assert(tick.remove_hook(M.magic_trick, 'slow'))
      end
   end
end


return M
