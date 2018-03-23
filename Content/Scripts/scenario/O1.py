import random

from unreal_engine import FVector, FRotator
from unreal_engine.classes import Screenshot

from scenario import base
from actors.parameters import ObjectParams
from tools.materials import get_random_material


class O1Base(object):
    @property
    def name(self):
        return 'O1'


class O1Train(O1Base, base.BaseTrain):
    def random_location(self, index, side=None):
        if side is None:
            side = 'left' if random.random() < 0.5 else 'right'

        return FVector(
            550 + 150 * float(index - 1),
            -500 if side == 'left' else 500,
            70 + 200 * random.random())

    def generate_parameters(self):
        params = super().generate_parameters()

        nobjects = 1  # random.randint(1, 3)
        for n in range(1, nobjects + 1):
            scale = 1.5 + random.random()
            params[f'object_{n}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=FVector(2000, 0, 0),  # self.random_location(n),
                rotation=FRotator(0, 0, 0),
                scale=FVector(scale, scale, scale),
                mass=100)

        return params


class O1TestStatic(O1Base, base.BaseTest):
    is_magic_actor_hidden = False

    def get_nchecks(self):
        if not self.is_occluded:
            return 0
        elif self.ntricks == 2:
            return 2
        else:  # occluded single trick
            return 1

    def random_location(self, index):
        # max scale is 1.5 (so width of 150), space between objects is
        # 170 so they are not overlapping
        return FVector(
            random.random() * 1000 + 500,
            170 * (index - 1),
            0)

    def generate_parameters(self):
        params = super().generate_parameters()

        nobjects = 1  # random.randint(1, 3)
        for n in range(1, nobjects + 1):
            # scale = 0.5 + random.random()
            scale = 1
            params[f'object_{n}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=FVector(500, 0, 110),  # self.random_location(n),
                rotation=FRotator(0, 0, 0),
                scale=FVector(scale, scale, scale),
                mass=100)

        params['magic'] = {
            'actor': f'object_{random.randint(1, nobjects)}',
            'tick': random.randint(10, 90)}

        return params

    def setup_magic_trick(self, actor, run):
        if run in (2, 4):
            self.is_magic_actor_hidden = True
            actor.set_hidden(self.is_magic_actor_hidden)

    def apply_magic_trick(self, actor, run):
        if run <= 2:
            actor.set_hidden(not actor.hidden)
            self.is_magic_actor_hidden = actor.hidden

    def get_ignored_actors(self):
        return []
