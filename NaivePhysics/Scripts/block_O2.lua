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

local main_object

local possible_shapes, current_shape_idx

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


local function swap_shapes()
   -- index of the new main actor (after swapping)
   local new_idx = current_shape_idx + 1
   if new_idx == 3 then new_idx = 1 end
   current_shape_idx = new_idx

   uetorch.SetActorStaticMesh(main_object, actors.get_mesh(possible_shapes[current_shape_idx]))

   if tick.get_counter() <= 1 then
      local f = params.objects[params.main_object].force
      uetorch.AddForce(main_object, f.x, f.y, f.z, true)
      --uetorch.AddForce(main_object, 0, 0, 0)
   end
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
   local nobjects = nobjects or math.random(1, 3)

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

   local t_objects, t_meshes = {}, {}
   for i = 1, nobjects do
      table.insert(t_objects, 'object_' .. i)
      table.insert(t_meshes, t_shapes[math.random(1, #t_shapes)])
   end

   local main_idx = math.random(1, nobjects)
   local main_object = t_objects[main_idx]
   local main_shape = t_meshes[main_idx]
   local other_shape = actors.get_different_shape(main_shape, t_shapes)

   local params = {}

   -- occluders
   if subblock:match('train') then
      params.occluders = occluders.get_random_parameters(math.random(0, 2))
   else
      local noccluders = #(M.get_occlusion_check_iterations(subblock)) / 2
      params.occluders = occluders.get_random_parameters(noccluders, subblock)
   end

   -- objects
   if subblock:match('train') then
      params.objects = actors.get_random_parameters(t_objects, t_meshes)
   else
      -- setup the actors parameters and the main actor (on which the
      -- trick is done)
      params.main_object = main_object
      params.other_shape = other_shape
      params.objects = {}

      for i = 1, nobjects do
         params.objects[t_objects[i]] = {}
         local p = params.objects[t_objects[i]]

         p.material = material.random('actor')
         local s = 1--0.7 + 0.5 * math.random()
         p.scale = {x = s, y = s, z = s}
         p.mesh = t_meshes[i]
         p.material = material.random('actor')
         p.rotation = {pitch = 0, yaw = 0, roll = 0}
         p.mass = 100  -- actors.mass_scale_normalization[p.mesh]

         if subblock:match('static') then
            local x_loc = {150, 40, 260}
            p.location = {x = x_loc[i], y = -550, z = 70}
            p.location.z = 100 * p.scale.x / 2.0 + 20
            p.force = {x = 0, y = 0, z = 0}

         elseif subblock:match('dynamic_1') then
            p.location = {x = -400, y = -550 - 150 * (i - 1), z = 100}
            p.force = {x = 2e4, y = 0, z = 1e4}-- {
            -- x = math.random(8e5, 1.1e6), y = 0,
            -- z = math.random(8e5, 1e6) * (2 * math.random(2) - 3)}

            if actors.random_side() == 'right' then
               p.location.x = 500
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
      is_possible = true
   elseif iteration.type == 2 then
      is_possible = true
   elseif iteration.type == 3 then
      is_possible = false
   elseif iteration.type == 4 then
      is_possible = false
   elseif iteration.type > 4 then  -- occlusion checks
      is_possible = true
   else  -- this is train
      assert(iteration.type == -1)
      is_possible = true
      return
   end

   -- on test, setup the main actor with the good shape
   main_object = actors.get_active_actors_normalized_names()[params.main_object]
   local main_shape = params.objects[params.main_object].mesh
   possible_shapes = {main_shape, params.other_shape}

   current_shape_idx = 1
   if iteration.type % 2 == 1 then
      swap_shapes()
      check_coordinates.set_reference_index(2)
   end

   -- on check occlusion iterations, keep alive a single occluder and
   -- the main actor (in either the first or second possible shapes)
   if subblock:match('occluded') and subblock:match('_2$') then
      if iteration.type > 4 and iteration.type <= 6 then
         occluders.destroy_normalized_name('occluder_2')
      elseif iteration.type > 6 and iteration.type <= 8 then
         occluders.destroy_normalized_name('occluder_1')
      end
   end

   if iteration.type > 4 then
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
               return utils.sign(params.trick_x - uetorch.GetActorLocation(main_object).x)
            end
            trick.can_do = function()
               if not trick.init_xdiff then trick.init_xdiff = trick.xdiff() end
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
   return actors.get_active_actors()
end


function M.magic_trick()
   -- if subblock:match('dynamic_2') then
   --    -- if not trick.is_done_1 and trick.can_do_1() then
   --    --    trick.is_done_1 = true
   --    --    uetorch.SetActorVisible(main_object, not is_visible_start)
   --    -- elseif trick.is_done_1 and not trick.is_done_2 and trick.can_do_2() then
   --    --    uetorch.SetActorVisible(main_object, is_visible_start)
   --    --    trick.is_done_2 = true
   --    --    tick.remove_hook(M.magic_trick, 'slow')
   --    -- end
   --    return
   -- else -- this is static or dynamic_1
   if not subblock:match('dynamic_2') then
      if not trick.is_done and trick.can_do() then
         swap_shapes()
         trick.is_done = true

         if subblock:match('dynamic_1') then
            if iteration.type == 4 then
               check_coordinates.set_reference_index(1)
            elseif iteration.type == 3 then
               check_coordinates.set_reference_index(2)
            end
         end
      end
   end
end


return M
