# import random

from unreal_engine import FVector, FRotator
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from scenario.run import RunPossible
# from unreal_engine.classes import ScreenshotManager


class SandBoxBase(Scene):
    def __init__(self, world, saver=None):
        super().__init__(world, saver)
        self.generate_parameters()
        for run in range(1):
            self.runs.append(RunPossible(
                self.world, saver, self.params, {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': True}))

    @property
    def name(self):
        return 'SandBox'


class SandBoxCamera(SandBoxBase):
    def generate_parameters(self):
        super().generate_parameters()
        locations = [FVector(1000 + 200 * y + 50, 0, 0) for y in (-1, 0, 1)]
        for object_nb in range(1):
            self.params[f'object_{object_nb + 1}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=locations[object_nb],
                rotation=FRotator(0, 0, 45),
                scale=FVector(3, 3, 3),
                mass=100,
                force=FVector(0, 0, 0))

    def play_run(self):
        super().play_run()
        actor = self.runs[self.run].actors['object_1']
        actor.set_force(FVector(-2e9, 0, 0))


class SandBoxOccluder(SandBoxBase):
    def generate_parameters(self):
        super().generate_parameters()

        self.params['occluder_1'] = OccluderParams(
            material=get_random_material('Wall'),
            location=FVector(400, 0, 0),
            rotation=FRotator(0, 0, 0),
            scale=FVector(1, 1, 1),
            moves=[0],
            warning=True,
            overlap=True,
            start_up=True,
            speed=1)

        self.params['occluder_2'] = OccluderParams(
            material=get_random_material('Wall'),
            location=FVector(600, 150, 0),
            rotation=FRotator(0, 0, 90),
            scale=FVector(1, 1, 1),
            moves=[0],
            warning=True,
            overlap=True,
            start_up=True,
            speed=1)

    def play_run(self):
        super().play_run()


SandBoxTrain = SandBoxOccluder


class SandBoxTest(SandBoxBase):
    pass
