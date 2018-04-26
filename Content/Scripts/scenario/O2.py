"""Bloc O2 is change of shape. Spheres, cubes and cones."""
import random

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
        magic_actor = self.params['magic']['actor']

        new_mesh = (self.params['magic']['mesh'] if is_magic_mesh
                    else self.params[magic_actor].mesh)
        self.runs[self.run].actors[magic_actor].set_mesh_str(
            Object.shape[new_mesh])
        Friction.SetMassScale(self.runs[self.run].actors[magic_actor].get_mesh(),
                              1)
        if 'Cube' in self.runs[self.run].actors[magic_actor].mesh_str:
            Friction.SetMassScale(self.runs[self.run].actors[magic_actor].get_mesh(),
                                  0.6155297517867)
        elif 'Cone' in self.runs[self.run].actors[magic_actor].mesh_str:
            Friction.SetMassScale(self.runs[self.run].actors[magic_actor].get_mesh(),
                                  1.6962973279499)

    def apply_magic_trick(self):
        # swap the mesh of the magic actor
        magic_actor = self.runs[self.run].actors[self.params['magic']['actor']]
        current_mesh = magic_actor.mesh_str.split('.')[-1]
        mesh_1 = self.params['magic']['mesh']
        mesh_2 = self.params[self.params['magic']['actor']].mesh
        new_mesh = mesh_1 if current_mesh == mesh_2 else mesh_2
        magic_actor.set_mesh_str(Object.shape[new_mesh])
