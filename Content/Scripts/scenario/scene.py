import random
import unreal_engine as ue
from unreal_engine import FVector, FRotator
from actors.parameters import SkySphereParams, FloorParams
from actors.parameters import LightParams, WallsParams, CameraParams
from tools.materials import get_random_material


class Scene:
    def __init__(self, world, saver):
        self.world = world
        self.params = {}
        self.generate_parameters()
        self.runs = []
        self.run = 0
        self.saver = saver

    def __del__(self):
        for run in self.runs:
            del run

    def get_status_header(self):
        """Return a dict describing the scenario"""
        status = {
            'name': self.name,
            'type':  'test' if 'Test' in type(self) else 'train',
            'is_possible': True if 'Check' in type(self.run)
            or 'Train' in type(self.run) else False}
        # TODO A check is possible since there is no magic trick (no ?)
        return status

    def get_status(self):
        """Return the current status of each moving actor in the scene"""
        return {k: v.get_status() for k, v in self.get_moving_actors().items()}

    def generate_parameters(self):
        self.params['Camera'] = CameraParams(
                location=FVector(0, 0, 200),
                rotation=FRotator(0, 0, 0))
        self.params['SkySphere'] = SkySphereParams()
        self.params['Floor'] = FloorParams(
                material=get_random_material('Floor'))
        self.params['Light'] = LightParams(
                type='SkyLight')
        prob_walls = 0.5
        if random.uniform(0, 1) <= prob_walls:
            self.params['Walls'] = WallsParams(
                    material=get_random_material('Wall'),
                    height=random.uniform(1, 5),
                    length=random.uniform(3000, 5000),
                    depth=random.uniform(1500, 5000))

    def play_run(self):
        if self.run >= len(self.runs):
            return
        ue.log("Run {}/{}: {} run".format(self.run + 1, len(self.runs), type(self.runs[self.run]).__name__[3:]))
        self.runs[self.run].play()
        self.saver.update_camera(self.runs[self.run].actors['Camera'])

    def is_over(self):
        if (self.run < len(self.runs)):
            return False
        return True

    def stop_run(self):
        if self.run >= len(self.runs):
            return
        self.runs[self.run].del_actors()
        self.run += 1

    def tick(self, tick_index):
        if (self.run < len(self.runs)):
            self.runs[self.run].tick(tick_index)
