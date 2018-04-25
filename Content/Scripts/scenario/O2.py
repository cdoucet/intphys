from scenario.test import Test
from scenario.train import Train
from unreal_engine.classes import Friction
from unreal_engine import FVector

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


class O2Test(O2Base, Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)

    def generate_parameters(self):
        super().generate_parameters()

    def apply_magic_trick(self):
        self.runs[self.run].actors[self.params['magic']['actor']].set_mesh_str('/Game/Meshes/Cube.Cube')
