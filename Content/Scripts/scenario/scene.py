import random
import os
import importlib
import unreal_engine as ue
from unreal_engine.classes import Friction
from unreal_engine import FVector, FRotator
from actors.parameters import FloorParams, WallsParams, CameraParams
from tools.materials import get_random_material
from actors.skysphere import Skysphere


class Scene:
    def __init__(self, world, saver):
        self.world = world
        self.params = {}
        self.saver = saver
        self.generate_parameters()
        self.actors = None
        self.run = 0
        self.last_locations = []
        self.status_header = {
                'name': self.name,
                'type': 'train' if 'Train' in type(self).__name__ else 'test',
                'is_possible': True if 'Trai' in type(self).__name__ else False
                }

    def get_status(self):
        """Return the current status of each moving actor in the scene"""
        # TODO change actors appearing in status :
        # Camera ? Walls ? Floor ? Skysphere ? ect.
        if self.actors is not None:
            return {k: v.get_status() for k, v in self.actors.items()}

    def generate_parameters(self):
        self.params['Camera'] = CameraParams(
                location=FVector(0, 0, 200),
                rotation=FRotator(0, 0, 0))
        """
        self.params['Skysphere'] = \
            SkysphereParams(rotation=FRotator(180, 180, 180))
        """
        self.params['Floor'] = FloorParams(
                material=get_random_material('Floor'))
        """
        self.params['Light'] = LightParams(
                type='SkyLight')
        """
        prob_walls = 0  # no walls to avoid luminosity problems
        if random.uniform(0, 1) <= prob_walls:
            self.params['Walls'] = WallsParams(
                    material=get_random_material('Wall'),
                    height=random.uniform(1, 5),
                    length=random.uniform(3000, 5000),
                    depth=random.uniform(1500, 3000))

    def play_run(self):
        if self.run == 0:
            self.spawn_actors()
            self.saver.update(self.actors)

    def is_valid(self):
        return all([a.is_valid for a in self.actors.values()])

    def spawn_actors(self):
        self.actors = {}
        for actor, actor_params in self.params.items():
            if ('magic' in actor):
                continue
            else:
                class_name = actor.split('_')[0].title()
            # dynamically import and instantiate
            # the class corresponding to the actor
            module_path = "actors.{}".format(actor.lower().split('_')[0])
            module = importlib.import_module(module_path)
            self.actors[actor] = getattr(module, class_name)(
                world=self.world, params=actor_params)
        """
        found_actors = self.world.all_actors()
        for actors in found_actors:
            actors.get_name()
        self.actors["Skysphere"] = \
            Skysphere(self.world, self.world.find_object("BP_Sky_Sphere"))
        """

    def reset_actors(self):
        if self.actors is None:
            return
        for name, actor in self.actors.items():
            if 'object' in name.lower() or 'occluder' in name.lower():
                actor.reset(self.params[name])

    def del_actors(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                actor.actor_destroy()
            self.actors = None

    def get_scene_subdir(self, scene_index, total):
        # build the scene sub-directory name, for exemple
        # '027_test_O1/3' or '028_train_O1' or '001_train_O1'
        idx = scene_index + 1
        # putting as much zeroes as necessary according
        # to the total number of scenes
        padded_idx = str(idx).zfill(len(str(total)))
        scene_name = (
            padded_idx + '_' +
            ('train' if 'Train' in type(self).__name__ else 'test') + '_' +
            self.name)
        out = os.path.join(self.saver.output_dir, scene_name)
        if 'Test' in type(self).__name__:
            # 1, 2, 3 and 4 subdirectories for test scenes
            run_idx = self.run + 1
            out = os.path.join(out, str(run_idx))
        return out

    def tick(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                if 'object' in actor_name or 'occluder' in actor_name:
                    actor.move()
