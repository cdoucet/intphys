import random

from unreal_engine import FVector, FRotator

from scenario import base
from actors.parameters import *
from tools.materials import get_random_material_for_category


class O1Base(object):
    @property
    def name(self):
        return 'O1'


class O1Train(O1Base, base.BaseTrain):
    def random_location(self, index, side=None):
        if side is None:
            side = 'left' if random.random() < 0.5 else 'right'

        return FVector(
            -400 if side == 'left' else 500,
            -550 - 150 * float(index - 1),
            70 + 200 * random.random())

    def generate_parameters(self):
        params = super().generate_parameters()

        nobjects = 1  #random.randint(1, 3)
        for n in range(1, nobjects+1):
            scale = 1.5 + random.random()
            params[f'object_{n}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material_for_category('Object'),
                location=FVector(0, 0, 0),  #self.random_location(n),
                rotation=FRotator(0, 0, 0),
                scale=FVector(scale, scale, scale),
                mass=100)

        return params


class O1Test(O1Base, base.BaseTest):
    def get_nchecks(self):
        nruns = 0
        if not self.is_occluded:
            nruns = 0
        elif self.ntricks == 2:
            nruns = 2
        else:  # occluded single trick
            nruns = 1
