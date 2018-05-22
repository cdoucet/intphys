import random
import math
import json
import os
import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager
from scenario.scene import Scene
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Friction
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from shutil import copyfile


class Test(Scene):
    def __init__(self, world, saver, is_occluded, movement):
        self.is_occluded = is_occluded
        self.movement = movement
        self.check_array = [{}, {}]
        self.ticker = 0
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()
        nobjects = random.randint(1, 3)
        if 'static' in self.movement:
            locations = [FVector(1000, 500 * y, 0) for y in (-1, 0, 1)]
        else:
            # random side for each actor: starting either from left
            # (go to right) or from rigth (go to left)
            locations = [FVector(1000 + 200 * y, -800
                                 if bool(random.getrandbits(1)) else 800, 0)
                         for y in (-1, 0, 1)]
            if '2' in self.movement:
                for location in locations:
                    if location.y < 0:
                        location.y = -600
                    else:
                        location.y = 600
        random.shuffle(locations)
        for n in range(nobjects):
            # scale in [1, 1.5]
            scale = 1 + random.uniform(0, 0.5)
            force = FVector(0, 0, 0)
            if 'static' not in self.movement:
                locations[n].x = locations[n].x + 50 * scale
            # full random rotation (does not matter on spheres, except
            # for texture variations)
            rotation = FRotator(
                360*random.random(), 360*random.random(), 360*random.random())
            self.params['object_{}'.format(n + 1)] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=locations[n],
                rotation=rotation,
                scale=FVector(scale, scale, scale),
                mass=1)
        self.params['magic'] = {
            'actor': f'object_{random.randint(1, nobjects)}',
            'tick': -1}

        if 'dynamic' in self.movement:
            self.initial_force = FVector()
        if self.is_occluded:
            moves = []
            scale = FVector(0.5, 1, 1.5)
            if 'dynamic' in self.movement:
                if '2' in self.movement:
                    location = FVector(600, -175, 0)
                else:
                    location = FVector(600, 0, 0)
                    scale.x = 1
                start_up = True
                moves.append(100)
            else:
                location = FVector(600, self.params[
                    self.params['magic']['actor']].location.y / 2, 0)
                scale.z = 1
                start_up = False
                moves.append(0)
                moves.append(100)
            self.params['occluder_1'] = OccluderParams(
                material=get_random_material('Wall'),
                location=location,
                rotation=FRotator(0, 0, 90),
                scale=scale,
                moves=moves,
                speed=1,
                start_up=start_up)
            if ('2' in self.movement):
                self.params['occluder_2'] = OccluderParams(
                    material=get_random_material('Wall'),
                    location=FVector(600, 175, 0),
                    rotation=FRotator(0, 0, 90),
                    scale=scale,
                    moves=moves,
                    speed=1,
                    start_up=start_up)

    def play_run(self):
        super().play_run()
        self.setup_magic_actor()
        if 'static' not in self.movement:
            for name, actor in self.actors.items():
                if 'object' in name.lower():
                    y_location = actor.actor.get_actor_location().y
                    force = FVector(0, -29e5 if y_location > 0 else 29e5, 0)
                    actor.set_force(force)

    def checks_time_laps(self, which, desired_bool):
        # looking for the state we want in the check
        # array of both run and put the corresponding frame in res array
        res = []
        nb = len(self.check_array[0][which])
        for frame in range(nb):
            # append True if both run's check_array are the desired bool
            # else False
            if (self.check_array[0][which][frame] ==
                    self.check_array[1][which][frame] and
                    self.check_array[1][which][frame] == desired_bool):
                res.append(frame)
        return res

    def magic_actor(self):
        return self.actors[self.params['magic']['actor']]

    def capture(self):
        ignored_actors = []
        if self.actors[self.params['magic']['actor']].hidden is True:
            ignored_actors.append(self.actors[self.params['magic']['actor']]
                                  .actor)
        self.saver.capture(ignored_actors, self.status_header,
                           self.get_status())

    def set_magic_tick(self):
        if self.is_occluded is True:
            if 'static' in self.movement:
                return self.static_occluded()
            elif 'dynamic_1' in self.movement:
                return self.dynamic_1_occluded()
            else:
                return self.dynamic_2_occluded()
        else:
            if 'static' in self.movement:
                return self.static_visible()
            elif 'dynamic_1' in self.movement:
                return self.dynamic_1_visible()
            else:
                return self.dynamic_2_visible()
