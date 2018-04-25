import random

from unreal_engine import FVector, FRotator
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from scenario.run import RunPossible
from unreal_engine.classes import ScreenshotManager


class SandBoxBase:
    def __init__(self, world, saver=None, is_occluded=None, movement=None):
        super().__init__(world, saver)
        self.generate_parameters()
        for run in range(1):
            self.runs.append(RunPossible(self.world, saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': True}
                ))

    @property
    def name(self):
        return 'SandBox'

    def tick(self, tick_index):
        super().tick(tick_index)
        if tick_index % 100 == 50:
            for name, actor in self.runs[0].actors.items():
                if 'object' in name.lower():
                    actor.set_force(FVector(0, -1e9, 7e8))

class SandBoxTrain(SandBoxBase, Scene):
    def generate_parameters(self):
        super().generate_parameters()
        locations = [FVector(1000 + 200 * y + 50, 500, 0) for y in (-1, 0, 1)]
        for object_nb in range(3):
            self.params[f'object_{object_nb + 1}'] = ObjectParams(
                    mesh='Cube',
                    material=get_random_material('Object'),
                    location=locations[object_nb],
                    rotation=FRotator(0, 0, 45),
                    scale=FVector(1, 1, 1),
                    mass=100,
                    force=FVector(0, 0, 0))
        """
        self.params['occluder'] = OccluderParams(
                material=get_random_material('Wall'),
                location=FVector(400, 0, 0),
                rotation=FRotator(0, 0, 90),
                scale=FVector(1, 1, 1),
                moves=[0],
                start_up=True,
                speed=1)
        """

    def play_run(self):
        super().play_run()


class SandBoxTest(SandBoxBase, Scene):
    pass
