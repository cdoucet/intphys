"""Block SandBox is apparition/disparition, spheres only"""
import random
import math
from unreal_engine import FVector, FRotator
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from scenario.test import Test
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
# import unreal_engine as ue


class SandBoxBase:
    @property
    def name(self):
        return 'SandBox'

    @property
    def description(self):
        return 'bloc SandBox'


class SandBoxTrain(SandBoxBase, Train):
    pass


class SandBoxTest(SandBoxBase, MirrorTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, False, "dynamic_1")

    def generate_parameters(self):
        Scene.generate_parameters(self)
        self.params['Object_1'] = ObjectParams()
        self.params['Object_1'].location = FVector(1250, 1250, 0)
        self.params['Object_2'] = ObjectParams()
        self.params['Object_2'].location = FVector(1500, 1500 + (self.params['Object_2'].scale.x * 100 * math.sqrt(2)), 0)
        self.params['Object_3'] = ObjectParams()
        self.params['Object_3'].location = FVector(2000, 2000 + (self.params['Object_3'].scale.x * 100 * math.sqrt(2)), 0)

    def setup_magic_actor(self):
        pass

    def play_magic_trick(self):
        pass
        magic = self.actors[self.params['magic']['actor']]
        magic.reset_force()
        magic.set_force(FVector(0, magic.initial_force.y * -1, 0))

    def fill_check_array(self):
        pass
        self.params['magic']['tick'] = 18

    def set_magic_tick(self):
        pass

    def tick(self):
        Scene.tick(self)
        for name, actor in self.actors.items():
            if 'object' in name and int(round(actor.actor.
                                        get_actor_velocity().y)) == 0:
                actor.set_force(actor.initial_force)
                break
        self.ticker += 1
