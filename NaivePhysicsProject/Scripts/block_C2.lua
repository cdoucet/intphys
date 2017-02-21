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
   'test_visible_static',
   -- 'test_visible_dynamic_1',
   -- 'test_visible_dynamic_2',
   'test_occluded_static',
   -- 'test_occluded_dynamic_1',
   -- 'test_occluded_dynamic_2'
}


local subblock

local iteration

local params

local main_actor, possible_main_actors, main_actor_idx

local is_possible

local is_shape1_start

local trick


local function is_valid_subblock(name)
   for _, subblock in ipairs(subblocks) do
      if name == subblock then
         return true
      end
   end
   return false
end


local function swap_actors()
   local new_idx = main_actor_idx + 1
   if new_idx == 3 then
      new_idx = 1
   end
   --   print(main_actor_idx, new_idx)
   local new_actor = possible_main_actors[new_idx]
   local old_actor = possible_main_actors[main_actor_idx]

   -- print('swapping ' .. actors.get_name(old_actor)
   --          .. ' to ' .. actors.get_name(new_actor))

   local new_l = uetorch.GetActorLocation(new_actor)
   local new_r = uetorch.GetActorRotation(new_actor)
   local new_v = uetorch.GetActorVelocity(new_actor)
   local new_a = uetorch.GetActorAngularVelocity(new_actor)

   local old_l = uetorch.GetActorLocation(old_actor)
   local old_r = uetorch.GetActorRotation(old_actor)
   local old_v = uetorch.GetActorVelocity(old_actor)
   local old_a = uetorch.GetActorAngularVelocity(old_actor)

   uetorch.SetActorLocation(old_actor, new_l.x, new_l.y, new_l.z)
   uetorch.SetActorRotation(old_actor, new_r.pitch, new_r.yaw, new_r.roll)
   uetorch.SetActorVelocity(old_actor, new_v.x, new_v.y, new_v.z)
   uetorch.SetActorAngularVelocity(old_actor, new_a.x, new_a.y, new_a.z)

   uetorch.SetActorLocation(new_actor, old_l.x, old_l.y, old_l.z)
   uetorch.SetActorRotation(new_actor, old_r.pitch, old_r.yaw, old_r.roll)
   uetorch.SetActorVelocity(new_actor, old_v.x, old_v.y, old_v.z)
   uetorch.SetActorAngularVelocity(new_actor, old_a.x, old_a.y, old_a.z)

   main_actor_idx = new_idx
   main_actor = new_actor
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
   local nactors = math.random(1, 3)

   local t_shapes = actors.get_shapes()
   local t_actors = {}
   for i = 1, nactors do
      table.insert(t_actors, t_shapes[math.random(1, #t_shapes)] .. '_' .. i)
   end
   local main_actor = t_actors[math.random(1, nactors)]
   local other_actor = actors.get_other_shape_actor(main_actor)


   local params = {}

   -- occluders
   if subblock:match('train') then
      params.occluders = occluders.get_random_parameters(math.random(0, 2))
   else
      local noccluders = #(M.get_occlusion_check_iterations(subblock))
      params.occluders = occluders.get_random_parameters(noccluders, subblock)
   end

   -- physics actors
   if subblock:match('train') then
      params.actors = actors.get_random_parameters(t_actors)
   else
      -- setup the actors parameters and the main actor (on which the
      -- trick is done)
      params.main_actor = main_actor
      params.other_actor = other_actor
      params.actors = {}

      for i = 1, nactors do
         params.actors[t_actors[i]] = {
            material = actors.random_material(),
            scale = 0.9}
         local p = params.actors[t_actors[i]]

         if subblock:match('static') then
            local x_loc = {150, 40, 260}
            p.location = {x = x_loc[i], y = -550, z = 70}
            p.scale = 1
         end
      end
      params.actors[other_actor] = {
         material = params.actors[main_actor].material,
         scale = params.actors[main_actor].scale,
         -- behind the camera
         location = {x = 0, y = 1000, z = 70}}

      -- setup the trick parameters for the visible subblocks (for
      -- occluded blocks this is done by the check_occlusion module)
      if subblock:match('visible') then
         if subblock:match('static') then
            -- the step at which the magic trick is done
            params.trick_step = math.floor((0.3*math.random() + 0.2) * config.get_nticks())
         end
      end
   end

   return params
end


function M.initialize(_subblock, _iteration, _params)
   subblock = _subblock
   iteration = _iteration
   params = _params

   if iteration.type == 1 then
      main_actor_idx = 2
      is_possible = true
   elseif iteration.type == 2 then
      main_actor_idx = 1
      is_possible = true
   elseif iteration.type == 3 then
      main_actor_idx = 2
      is_possible = false
   elseif iteration.type == 4 then
      main_actor_idx = 1
      is_possible = false
   else  -- this includes iterations for train and occlusion checks
      main_actor_idx = 1
      is_possible = true
   end

   -- on train iteration we have no more job
   if iteration.type == -1 then
      return
   end

   -- on test, setup the main actor
   possible_main_actors = {
      actors.get_actor(assert(params.main_actor)),
      actors.get_actor(assert(params.other_actor))}

   if main_actor_idx == 2 then
      swap_actors()
   end
   main_actor = possible_main_actors[main_actor_idx]

   -- initialize the ticking method that do the magic stuff
   if not M.is_possible() then
      tick.add_hook(M.magic_trick, 'slow')

      -- setup the trick data
      if subblock:match('dynamic_2') then
         return
      else  -- dynamic_1 or static
         trick = {is_done = false}

         if subblock:match('occluded') then
            trick.can_do = function()
               return check_occlusion.is_middle_of_two_occlusions(5, 6) end
         elseif subblock:match('static') then -- visible static
            trick.can_do = function()
               return tick.get_counter() == assert(params.trick_step) end
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
      local idx = 2
      if s:match('_2$') then idx = 4 end
      for i = idx, 1, -1 do
         table.insert(it, 4 + i)
      end
      return it
   end
end


function M.is_main_actor_visible()
   return true
end


function M.magic_trick()
   -- if subblock:match('dynamic_2') then
   --    -- if not trick.is_done_1 and trick.can_do_1() then
   --    --    trick.is_done_1 = true
   --    --    uetorch.SetActorVisible(main_actor, not is_visible_start)
   --    -- elseif trick.is_done_1 and not trick.is_done_2 and trick.can_do_2() then
   --    --    uetorch.SetActorVisible(main_actor, is_visible_start)
   --    --    trick.is_done_2 = true
   --    --    tick.remove_hook(M.magic_trick, 'slow')
   --    -- end
   --    return
   -- else -- this is static or dynamic_1

   if not trick.is_done and trick.can_do() then
      swap_actors()
      trick.is_done = true
      tick.remove_hook(M.magic_trick, 'slow')
   end
end


return M
