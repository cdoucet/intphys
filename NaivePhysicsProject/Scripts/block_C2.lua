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
local check_coordinates = require 'check_coordinates'


local subblocks = {
   'train',
   'test_visible_static',
   'test_visible_dynamic_1',
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


-- swap the main actor between the possible_main_actors
local function swap_actors()
   local new_idx = main_actor_idx + 1
   if new_idx == 3 then
      new_idx = 1
   end

   local new_actor = possible_main_actors[new_idx]
   local old_actor = possible_main_actors[main_actor_idx]

   local l = uetorch.GetActorLocation(old_actor)
   -- local r = uetorch.GetActorRotation(old_actor)
   -- local v = uetorch.GetActorVelocity(old_actor)
   -- local a = uetorch.GetActorAngularVelocity(old_actor)

   uetorch.SetActorVisible(old_actor, false)
   uetorch.SetActorLocation(old_actor, 0, 1000, 70)

   uetorch.SetActorLocation(new_actor, l.x, l.y, l.z)
   -- uetorch.SetActorRotation(new_actor, r.pitch, r.yaw, r.roll)
   -- uetorch.SetActorVelocity(new_actor, v.x, v.y, v.z)
   -- uetorch.SetActorAngularVelocity(new_actor, a.x, a.y, a.z)
   uetorch.SetActorVisible(new_actor, true)

   main_actor_idx = new_idx
   main_actor = new_actor
   check_coordinates.change_actor(main_actor)
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

   -- exclude cylinders for static tests because they can have a cube
   -- or sphere profile
   local t_shapes = actors.get_shapes()
   if subblock:match('static') then
      for k, v in ipairs(t_shapes) do
         if v == 'cylinder' then
            table.remove(t_shapes, k)
            break
         end
      end
   end

   local t_actors = {}
   for i = 1, nactors do
      table.insert(t_actors, t_shapes[math.random(1, #t_shapes)] .. '_' .. i)
   end
   local main_actor = t_actors[math.random(1, nactors)]
   local other_actor = actors.get_other_shape_actor(main_actor, t_shapes)

   local params = {}

   -- occluders
   if subblock:match('train') then
      params.occluders = occluders.get_random_parameters(math.random(0, 2))
   else
      local noccluders = #(M.get_occlusion_check_iterations(subblock)) / 2
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
         params.actors[t_actors[i]] = {}
         local p = params.actors[t_actors[i]]

         p.material = material.random('actor')
         p.scale = 1 --0.9

         if subblock:match('static') then
            local x_loc = {150, 40, 260}
            p.location = {x = x_loc[i], y = -550, z = 70}
            p.scale = 1
         elseif subblock:match('dynamic_1') then
            p.location = {x = -400, y = -350 - 150 * (i - 1), z = 70 + math.random(200)}
            p.force = {
               x = math.random(8e5, 1.1e6), y = 0,
               z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

            if actors.random_side() == 'right' then
               p.location.x = 500
               p.force.x = -1 * p.force.x
            end
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
         elseif subblock:match('dynamic_1') then
            -- the x position on which the magic trick is done
            params.trick_x = math.random()*250 + 50
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
   elseif iteration.type > 4 then  -- occlusion checks
      is_possible = true
      if iteration.type % 2 == 0 then
         main_actor_idx = 1
      else
         main_actor_idx = 2
      end
   else  -- this is train
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

   main_actor = possible_main_actors[main_actor_idx]
   local other_actor_idx = main_actor_idx + 1
   if other_actor_idx == 3 then other_actor_idx = 1 end
   uetorch.SetActorVisible(possible_main_actors[other_actor_idx], false)

   if main_actor_idx == 2 then
      main_actor_idx = 1
      swap_actors()
   end

   -- on check occlusion iterations, keep alive a single occluder and
   -- the main actor (in either the first or second possible shapes)
   if iteration.type > 4 and iteration.type <= 6 then
      uetorch.DestroyActor(occluders.get_occluder('occluder_2'))
   elseif iteration.type > 6 and iteration.type <= 8 then
      uetorch.DestroyActor(occluders.get_occluder('occluder_1'))
   end

   if iteration.type > 4 then
      for n, a in pairs(actors.get_active_actors()) do
         if n ~= actors.get_name(main_actor) then
            uetorch.DestroyActor(a)
         end
      end
   end

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
         else -- visible dynamic_1
            trick.init_xdiff = nil
            trick.xdiff = function()
               return utils.sign(params.trick_x - uetorch.GetActorLocation(main_actor).x)
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
      local idx = 2
      if s:match('_2$') then idx = 4 end
      for i = idx, 1, -1 do
         table.insert(it, 4 + i)
      end
      return it
   end
end


function M.get_active_actors()
   local idx = 2
   if main_actor_idx == 2 then
      idx = 1
   end

   local a = {}
   for name, actor in pairs(actors.get_active_actors()) do
      if actor ~= possible_main_actors[idx] then
         a[name] = actor
      end
   end

   return a
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
   if subblock:match('static') then
      if not trick.is_done and trick.can_do() then
         swap_actors()
         trick.is_done = true

         -- TODO do not work: we have a black screenshot for the 3
         -- images, only for C2
         -- tick.remove_hook(M.magic_trick, 'slow')
      end
   end
end


return M
