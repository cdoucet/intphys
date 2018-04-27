"""Bloc O2 is change of shape. Spheres, cubes and cones."""
import random
import math
import unreal_engine as ue
from actors.object import Object
from scenario.test import Test
from scenario.train import Train
from unreal_engine.classes import Friction
from unreal_engine import FRotator


class O2Base:
    @property
    def name(self):
        return 'O2'

    @property
    def description(self):
        return 'bloc O2'


class O2Train(O2Base, Train):
    def __init__(self, world, saver):
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()

        for name, params in self.params.items():
            if 'object' in name:
                # objects can be of any shapes, not only sphere
                params.mesh = random.choice(list(Object.shape.keys()))


class O2Test(O2Base, Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)

    def generate_parameters(self):
        super().generate_parameters()

        for name, params in self.params.items():
            if 'object' in name:
                # objects can be of any shapes, not only sphere
                params.mesh = random.choice(list(Object.shape.keys()))

                # force the rotation to be 0 (roll excepted)
                params.rotation = FRotator(0, 0, 360*random.random())

        # specify an alternative mesh for the magic actor (different
        # from the original one)
        magic_actor = self.params['magic']['actor']
        magic_mesh = self.params[magic_actor].mesh
        new_mesh = random.choice(
            [m for m in Object.shape.keys() if m != magic_mesh])
        self.params['magic']['mesh'] = new_mesh

    def setup_magic_actor(self):
        # on run 1 and 3 the magic actor mesh is
        # self.params[magic_actor].mesh at start, on runs 2 and 4 it
        # is self.params['magic']['mesh'] (runs 1, 2 are impossible,
        # runs 3, 4 are possible).
        run = self.run - self.get_nchecks() + 1
        is_magic_mesh = True if run in (2, 4) else False
        magic_actor_type = self.params['magic']['actor']
        magic_actor = self.runs[self.run].actors[magic_actor_type]

        new_mesh = (self.params['magic']['mesh'] if is_magic_mesh
                    else self.params[magic_actor_type].mesh)
        magic_actor.set_mesh_str(Object.shape[new_mesh])

        Friction.SetMassScale(magic_actor.get_mesh(), 1)

        if 'Cube' in magic_actor.mesh_str:
            Friction.SetMassScale(magic_actor.get_mesh(), 0.6155297517867)

        elif 'Cone' in magic_actor.mesh_str:
            Friction.SetMassScale(magic_actor.get_mesh(), 1.6962973279499)

    def apply_magic_trick(self):
        # swap the mesh of the magic actor
        magic_actor = self.runs[self.run].actors[self.params['magic']['actor']]
        current_mesh = magic_actor.mesh_str.split('.')[-1]
        mesh_1 = self.params['magic']['mesh']
        mesh_2 = self.params[self.params['magic']['actor']].mesh
        new_mesh = mesh_1 if current_mesh == mesh_2 else mesh_2
        magic_actor.set_mesh_str(Object.shape[new_mesh])

    def static_visible(self, check_array):
        count = 0
        while count < 50:
            count += 1
            magic_tick = random.randint(50, 150)
            # check if actor is not visible during magic tick
            if check_array[magic_tick][0] is not True:
                continue
            self.params['magic']['tick'] = magic_tick
            return True
        ue.log_warning("to many try to find a magic tick")
        return False

    def dynamic_1_visible(self, check_array):
        grounded_changes = self.process(1, check_array)
        if len(grounded_changes) < 2:
            ue.log_warning("not enough grounded changes")
            return False
        magic_tick = math.ceil((grounded_changes[1] + grounded_changes[0]) / 2)
        # check if actor is not visible during magic tick
        if check_array[magic_tick][0] is not True:
            ue.log_warning("actor was not visible during magic trick")
            return False
        self.params['magic']['tick'] = magic_tick
        return True

    def dynamic_2_visible(self, check_array):
        grounded_changes = self.process(1, check_array)
        if len(grounded_changes) < 2:
            ue.log_warning("not enough grounded changes")
            return False
        middle = math.ceil((grounded_changes[1] + grounded_changes[0]) / 2)
        magic_tick = math.ceil((middle + grounded_changes[0]) / 2)
        magic_tick2 = math.ceil((middle + grounded_changes[1]) / 2)
        # check if actor is not visible during magic tick
        if check_array[magic_tick][0] is not True and \
                check_array[magic_tick2][0] is not True:
            ue.log_warning("magic actor was not visible during magic trick")
            return False
        self.params['magic']['tick'][0] = magic_tick
        self.params['magic']['tick'][1] = magic_tick2
        return True

    def static_occluded(self, check_array):
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 2:
            ue.log_warning("not enough visibility changes")
            return False
        magic_tick = math.ceil((visibility_changes[1] + visibility_changes[0]) / 2)
        self.params['magic']['tick'] = magic_tick
        return True

    def dynamic_1_occluded(self, check_array):
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 2:
            ue.log_warning("not enough visibility changes")
            return False
        magic_tick = math.ceil((visibility_changes[1] + visibility_changes[0]) / 2)
        if check_array[magic_tick][1] is True:
            ue.log_warning("the actor was grounded during magic trick")
            return False

    def dynamic_2_occluded(self, check_array):
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 4:
            ue.log_warning("not enough visibility changes")
            return False
        magic_tick = math.ceil((visibility_changes[1] + visibility_changes[0]) / 2)
        magic_tick2 = math.ceil((visibility_changes[2] + visibility_changes[3]) / 2)
        # check is actor is in the air for both magic ticks
        if check_array[magic_tick][1] is True or \
                check_array[magic_tick2][1] is True:
            ue.log_warning("the actor was grounded during magic trick")
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(magic_tick)
        self.params['magic']['tick'].append(magic_tick2)
        return True

    def set_magic_tick(self, check_array):
        try:
            if self.is_occluded is True:
                if 'static' in self.movement:
                    return self.static_occluded(check_array)
                elif 'dynamic_1' in self.movement:
                    return self.dynamic_1_occluded(check_array)
                else:
                    return self.dynamic_2_occluded(check_array)
            else:
                if 'static' in self.movement:
                    return self.static_visible(check_array)
                elif 'dynamic_1' in self.movement:
                    return self.dynamic_1_visible(check_array)
                else:
                    return self.dynamic_2_visible(check_array)
        except Exception as e:
            ue.log_warning(e)
            return False
