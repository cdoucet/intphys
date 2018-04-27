import random
import math
import os
import unreal_engine as ue
from scenario.scene import Scene
from scenario.run import Run
from unreal_engine import FVector, FRotator
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from shutil import copyfile


class Test(Scene):
    def __init__(self, world, saver, is_occluded, movement):
        self.is_occluded = is_occluded
        self.movement = movement
        self.magic_locations = [[],[]]
        super().__init__(world, saver)
        """
        for run in range(self.get_nchecks()):
            self.runs.append(RunCheck(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': True}
                ))
        for run in range(2):
            self.runs.append(RunImpossible(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': False}
                ))
        """
        for run in range(2):
            self.runs.append(Run(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': True}
                , True))

    def get_nchecks(self):
        res = 0
        if self.is_occluded is True:
            res += 1
            if 'dynamic_2' in self.movement:
                res += 1
        return 0
        return res

    def generate_parameters(self):
        super().generate_parameters()
        nobjects = random.randint(1, 3)
        # TODO remove next line it's here only for test
        nobjects = 3
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
            scale = 1# + random.random()
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
            scale = FVector(1, 1, 1.5)
            if 'dynamic' in self.movement:
                if self.movement.split('_')[1] == '2':
                    location = FVector(600, -175, 0)
                    scale.x = 0.5
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
            if ('dynamic' in self.movement and
                    self.movement.split('_')[1] == '2'):
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
            for name, actor in self.runs[self.run].actors.items():
                if 'object' in name.lower():
                    y_location = actor.actor.get_actor_location().y
                    force = FVector(0, -29e5 if y_location > 0 else 29e5, 0)
                    if 'O2' in type(self).__name__:
                        force.z = 24e5
                    actor.set_force(force)

    def stop_run(self, scene_index):
        if self.run >= len(self.runs):
            return True
        if self.set_magic_tick(self.runs[self.run].del_actors()) is False or self.runs[self.run].b_is_valid is False:
            return False
        super().stop_run(scene_index)
        if self.run == 2  + self.get_nchecks() and self.saver.is_dry_mode is False:
            self.generate_magic_runs(scene_index)

    def tick(self):
        super().tick()
        magic_tick = self.params['magic']['tick']
        if isinstance(magic_tick, int):
            magic_tick = [magic_tick]

        self.magic_locations[self.run].append(self.runs[self.run].actors[self.params['magic']['actor']].actor.get_actor_location())

    def generate_magic_runs(self, scene_index):
        if '2' not in self.movement:
            magic_tick = math.ceil((self.params['magic']['tick'] + 1) / 2)
            magic_tick2 = 100
            ue.log("magic tick = {}".format(magic_tick))
        else:
            magic_tick = math.ceil((self.params['magic']['tick'][0] + 1) / 2) + 1
            magic_tick2 = math.ceil((self.params['magic']['tick'][1] + 1) / 2) + 1
            ue.log("magic ticks = {} - {}".format(magic_tick, magic_tick2))
        # TODO make the same thing for the status.json
        # next line is removing the run subdirectory from the path
        subdir = self.get_scene_subdir(scene_index)[:-2]
        pic_types = ["scene", "depth", "masks"]
        for pic_type in pic_types:
            if not os.path.exists("{}/3/{}".format(subdir, pic_type)):
                os.makedirs("{}/3/{}".format(subdir, pic_type))
            for i in range(1, magic_tick + 1):
                dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)
            for i in range(magic_tick, magic_tick2 + 1):
                dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)
            if '2' in self.movement:
                for i in range(magic_tick2, 101):
                    dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                    src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                    copyfile(src, dst)
        for pic_type in pic_types:
            if not os.path.exists("{}/4/{}".format(subdir, pic_type)):
                os.makedirs("{}/4/{}".format(subdir, pic_type))
            for i in range(1, magic_tick + 1):
                dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)
            for i in range(magic_tick, magic_tick2 + 1):
                dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)
            if '2' in self.movement:
                for i in range(magic_tick2, 101):
                    dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                    src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                    copyfile(src, dst)

    def is_possible(self):
        return True if self.run_index - self.get_nchecks() in (3, 4) else False

    def process(self, which, check_array):
        res = []
        for frame_index in range(len(check_array) - 1):
            if (frame_index > 0 and
                    check_array[frame_index - 1][which] !=
                    check_array[frame_index][which]):
                res.append(frame_index)
        return res
