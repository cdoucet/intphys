import random
import math
import json
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
        if 'static' in self.movement:
            locations = [FVector(1000, 500 * y, 0) for y in (-1, 0, 1)]
        else:
            # random side for each actor: starting either from left
            # (go to right) or from rigth (go to left)
            locations = [FVector(1000 + 200 * y, -800
                                 if bool(random.getrandbits(1)) else 800, 0)
                         for y in (-1, 0, 1)]
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
            if 'dynamic' in self.movement:
                if self.movement.split('_')[1] == '2':
                    location = FVector(600, -300, 0)
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
                scale=FVector(1, 1, 1.5),
                moves=moves,
                speed=1,
                start_up=start_up)
            if ('dynamic' in self.movement and
                    self.movement.split('_')[1] == '2'):
                self.params['occluder_2'] = OccluderParams(
                    material=get_random_material('Wall'),
                    location=FVector(600, 300, 0),
                    rotation=FRotator(0, 0, 90),
                    scale=FVector(1, 1, 1.5),
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
                    force = FVector(0, -27e5 if y_location > 0 else 27e5, 0)
                    if 'O2' in type(self).__name__:
                        force.z = 24e5
                    actor.set_force(force)

    def stop_run(self, scene_index):
        if self.run >= len(self.runs):
            return True
        if self.set_magic_tick(self.runs[self.run].del_actors()) is False or self.runs[self.run].b_is_valid is False:
            return False
        super().stop_run(scene_index)
        if self.run == 2 + self.get_nchecks() and self.saver.is_dry_mode is False:
            self.generate_magic_runs(scene_index)

    def tick(self):
        super().tick()
        magic_tick = self.params['magic']['tick']
        if isinstance(magic_tick, int):
            magic_tick = [magic_tick]

        self.magic_locations[self.run].append(
            self.magic_actor().actor.get_actor_location())

        # if self.run == 0:
        #     self.magic_locations.append(self.magic_actor().actor.get_actor_location())
        # elif self.magic_actor().actor.get_actor_location() != self.magic_locations[self.runs[self.run].ticker - 1]:
        #     self.runs[self.run].b_is_valid = False
        # if (self.magic_locations[self.run] != self.magic_locations[self.run - 1]):
        #     ue.log("Magic locations don't match")
        #     self.runs[self.run].del_actors()
        #     self.runs[self.run].b_is_valid = False

    def generate_magic_runs(self, scene_index):
        ue.log('generating magic runs')

        magic_tick = math.ceil((self.params['magic']['tick'] + 1) / 2)
        ue.log(f'magic tick = {magic_tick}')

        # remove the run subdirectory from the path
        subdir = self.get_scene_subdir(scene_index)[:-2]

        pic_types = ["scene", "depth", "masks"]
        for pic_type in pic_types:
            if not os.path.exists("{}/3/{}".format(subdir, pic_type)):
                os.makedirs("{}/3/{}".format(subdir, pic_type))
            for i in range(1, magic_tick + 1):
                dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)
            for i in range(magic_tick, 101):
                dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)

        for pic_type in pic_types:
            if not os.path.exists("{}/4/{}".format(subdir, pic_type)):
                os.makedirs("{}/4/{}".format(subdir, pic_type))
            for i in range(1, magic_tick + 1):
                dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)
            for i in range(magic_tick, 101):
                dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type, str(i).zfill(3))
                copyfile(src, dst)

        # build the status.json
        self.generate_magic_status(subdir, [magic_tick])

    def generate_magic_status(self, subdir, slice_index):
        # build the status.json, slice_index are magic_tick as a list
        json_1 = json.load(open(f'{subdir}/1/status.json', 'r'))
        json_2 = json.load(open(f'{subdir}/2/status.json', 'r'))

        # the headers must be the same (excepted the actor names but do
        # not impact the end user) TODO for now (as of commit e5e2c25) the
        # 'masks' entry is different in runs 1 and 2 TODO to have same
        # names, maybe change the runs implementation: spawn actors only
        # at scene init, and destroy them at scene end but not between 2
        # runs.
        json_3 = {'header': json_1['header']}
        json_4 = {'header': json_1['header']}
        json_3['header']['is_possible'] = False
        json_4['header']['is_possible'] = False

        # update the frames according to the slice index
        f1, f2 = json_1['frames'], json_2['frames']
        if len(slice_index) == 2:  # dynamic_2 case
            idx1, idx2 = slice_index[0], slice_index[1]
            json_3['frames'] = f1[:idx1] + f2[idx1:idx2] + f1[idx2:]
            json_4['frames'] = f2[:idx1] + f1[idx1:idx2] + f2[idx2:]
        else:  # dynamic_1 or static cases
            idx = slice_index[0]
            json_3['frames'] = f1[:idx] + f2[idx:]
            json_4['frames'] = f2[:idx] + f1[idx:]

        # make sure the dest directories exist
        for i in (3, 4):
            d = f'{subdir}/{i}'
            if not os.path.isdir(d):
                os.makedirs(d)

        # save the status as JSON files
        with open(f'{subdir}/3/status.json', 'w') as fin:
            fin.write(json.dumps(json_3, indent=4))
        with open(f'{subdir}/4/status.json', 'w') as fin:
            fin.write(json.dumps(json_4, indent=4))

        # print('\n'.join('{} {}'.format(
        #     f3[magic_object]['material'], f4[magic_object]['material'])
        #     for f3, f4 in zip(json_3['frames'], json_4['frames'])))

    def is_possible(self):
        return True if self.run_index - self.get_nchecks() in (3, 4) else False

    def process(self, which, check_array):
        # TODO comment
        res = []
        for frame_index in range(len(check_array) - 1):
            if (frame_index > 0 and
                    check_array[frame_index - 1][which] !=
                    check_array[frame_index][which]):
                res.append(frame_index)
        return res

    def magic_actor(self):
        return self.runs[self.run].actors[self.params['magic']['actor']]

    def capture(self):
        """Overload of Scene.capture to ignore magic actor when hidden"""
        run = self.runs[self.run]

        # on O1 test we need to ignore the magic actor when it is
        # hidden (to ignore it on depth and masks images)
        if self.magic_actor().hidden:
            ignored = [self.magic_actor().actor]
        else:
            ignored = []
        run.capture(ignored_actors=ignored)

    def set_magic_tick(self, check_array):
        if self.is_occluded is False:
            # try to get a tick where the magic actor is visible, do
            # it 50 times or fail TODO built the list of visible ticks
            # and take a random one in it.
            count = 0
            while count < 50:
                count += 1
                self.params['magic']['tick'] = random.randint(50, 150)
                if check_array[self.params['magic']['tick']][0] is not True:
                    continue
                return True
            return False

        # in occluded case the magic tick is at the middle of the
        # occlusion time. TODO check if only one state changment would
        # be enough
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 2:
            ue.log('check failed: bad occlusion')
            return False
        if '2' in self.movement:
            pass
        else:
            magic_tick = math.ceil(
                (visibility_changes[1] + visibility_changes[0]) / 2)
        self.params['magic']['tick'] = magic_tick
        return True
