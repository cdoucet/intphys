"""The scene's floor has a fixed mesh, position and scale, with a
random material

"""

import random
import unreal_engine as ue

from unreal_engine import FVector, FRotator

from actors.abstract_actor import BaseActor
from materials import load_materials, get_random_material


class Floor(BaseActor):
    floor_materials = load_materials('Materials/Floor')

    def __init__(self):
        super(Floor, self).__init__()

        self.params = {
            'mesh': '/Game/Meshes/Floor_400x400',
            'material': get_random_material(self.floor_materials),
            'location': FVector(-200, -720, 0),
            'rotation': FRotator(0, 0, 0),
            'scale': FVector(10, 10, 1)
        }
