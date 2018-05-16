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
            scale = 1  # + random.random()
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

        # magic tick is determined by the checks when occluded
        if self.is_occluded:
            tick = -1
        elif '_2' in self.movement:
            # non occluded with 2 magic changes at different ticks
            tick = [random.randint(25, 40), random.randint(60, 75)]
        else:
            # non occluded with a single magic change
            tick = random.randint(25, 75)

        self.params['magic'] = {
            'actor': f'object_{random.randint(1, nobjects)}',
            'tick': tick}

        if 'dynamic' in self.movement:
            self.initial_force = FVector()
        if self.is_occluded:
            moves = []
            scale = FVector(0.5, 1, 1.5)
            if 'dynamic' in self.movement:
                if self.movement.split('_')[1] == '2':
                    location = FVector(600, -175, 0)
                else:
                    location = FVector(600, 0, 0)
                start_up = True
                moves.append(100)
            else:
                location = FVector(400, self.params[
                    self.params['magic']['actor']].location.y / 2, 0)
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
        if self.run == 4:
            return
        ue.log("Run {}/4: Possible run".format(self.run + 1))
        super().play_run()
        self.setup_magic_actor()
        if 'static' not in self.movement:
            for name, actor in self.actors.items():
                if 'object' in name.lower():
                    y_location = actor.actor.get_actor_location().y
                    force = FVector(0, -29e5 if y_location > 0 else 29e5, 0)
                    if 'O2' in type(self).__name__:
                        force.z = 24e5
                    actor.set_force(force)

    def stop_run(self, scene_index):
        self.ticker = 0
        if self.run == 1 and self.set_magic_tick() is False:
            self.del_actors()
            return False
        if self.run != 3:
            self.reset_actors()
        else:
            self.del_actors()
        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index))
            # reset actors if it is the last run
            self.saver.reset(True if self.run == 3 else False)
        self.run += 1
        return True

    def tick(self):
        super().tick()
        if self.run <= 1:
            self.fill_check_array()
        elif isinstance(self.params['magic']['tick'], int) and \
                self.ticker == self.params['magic']['tick']:
            self.play_magic_trick()
        elif not isinstance(self.params['magic']['tick'], int) and \
                self.ticker in self.params['magic']['tick']:
            self.play_magic_trick()
        self.ticker += 1

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
            ignored_actors.append(self.actors[self.params['magic']['actor']].actor)
        self.saver.capture(ignored_actors, self.status_header, self.get_status())

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

    def is_over(self):
        return True if self.run == 4 else False
