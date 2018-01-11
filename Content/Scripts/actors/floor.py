"""The scene's floor has a fixed mesh, position and scale, with a
random material

"""

import random
import unreal_engine as ue

from actors.abstract_actor import BaseActor
from unreal_engine import FVector, FRotator


class Floor(BaseActor):
    # TODO cannot use get_assets() since it works only in the editor,
    # try with ue.load_class for each file in the directory
    floor_materials = ue.get_assets('/Game/Materials/Floor')

    def __init__(self):
        super(Floor, self).__init__()
        random.shuffle(self.floor_materials)

        self.params = {
            'mesh': '/Game/Meshes/Floor_400x400',
            'material': self.floor_materials[0],
            'location': FVector(-200, -720, 0),
            'rotation': FRotator(0, 0, 0),
            'scale': FVector(10, 10, 1)
        }
