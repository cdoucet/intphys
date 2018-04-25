import random
import os
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
        ue.log("Run {}/{}: {} run".format(self.run + 1, len(self.runs),
                                          type(self.runs[self.run]).
                                          __name__[3:]))
        self.runs[self.run].play()

    def is_over(self):
        if (self.run < len(self.runs)):
            return False
        return True

    def stop_run(self, scene_index):
        if self.run >= len(self.runs):
            return True
        if 'Check' not in type(self.runs[self.run]).__name__ and \
                self.saver.is_dry_mode is False:
            self.saver.save(self.get_scene_subdir(scene_index))
            self.saver.reset()
        self.runs[self.run].del_actors()
        self.run += 1
        return True

    def get_scene_subdir(self, scene_index):
        # build the scene sub-directory name, for exemple
        # '027_test_O1/3' or '028_train_O1'
        idx = scene_index + 1
        padded_idx = '0{}'.format(idx)
        scene_name = (
                padded_idx + '_' +
                ('train' if 'Train' in type(self).__name__ else 'test') + '_' +
                self.name)
        out = os.path.join(self.saver.output_dir, scene_name)
        if 'Test' in type(self).__name__:
            # 1, 2, 3 and 4 subdirectories for test scenes
            run_idx = (self.run + 1) - self.get_nchecks()
            out = os.path.join(out, str(run_idx))
        return out

    def capture(self):
        if 'Check' not in type(self.runs[self.run]).__name__ and \
                self.saver.is_dry_mode is False:
            self.runs[self.run].capture()

    def tick(self):
        if (self.run < len(self.runs)):
            self.runs[self.run].tick()
