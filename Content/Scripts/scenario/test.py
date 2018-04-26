import random
import math
import os
import unreal_engine as ue
from scenario.scene import Scene
from scenario.run import RunCheck, RunPossible, RunImpossible
from unreal_engine import FVector, FRotator
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from shutil import copyfile


class Test(Scene):
    def __init__(self, world, saver, is_occluded, movement):
        self.is_occluded = is_occluded
        self.movement = movement
        super().__init__(world, saver)
        for run in range(self.get_nchecks()):
            self.runs.append(RunCheck(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': True}
                ))
        """
        for run in range(2):
            self.runs.append(RunImpossible(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': False}
                ))
        """
        for run in range(2):
            self.runs.append(RunPossible(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': True}
                ))

    def get_nchecks(self):
        res = 0
        if self.is_occluded is True:
            res += 1
            if 'dynamic_2' in self.movement:
                res += 1
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
            scale = 1 + random.random()
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

    def set_magic_tick(self, change_state):
        # it is always an occluded test if you are here
        # TODO check if only one state changment would be enough
        if len(change_state) < 2:
            return False
        if '2' in self.movement:
            pass
        else:
            magic_tick = math.ceil((change_state[1] + change_state[0]) / 2)
        self.params['magic']['tick'] = magic_tick
        for run in self.runs:
            if (type(run) is RunImpossible):
                run.actors_params['magic']['tick'] = magic_tick
        return True

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
        if (type(self.runs[self.run]) is RunCheck):
            if self.set_magic_tick(self.runs[self.run].del_actors()) is False:
                return False
        else:
            self.runs[self.run].del_actors()
        super().stop_run(scene_index)
        if self.run == 2  + self.get_nchecks() and self.saver.is_dry_mode is False:
            self.generate_magic_runs(scene_index)

    def tick(self):
        super().tick()
        magic_tick = self.params['magic']['tick']
        if isinstance(magic_tick, int):
            magic_tick = [magic_tick]

        if self.runs[self.run].ticker in magic_tick \
           and type(self.runs[self.run]) is RunImpossible:
            ue.log("tick {}: magic trick".format(self.runs[self.run].ticker))
            self.apply_magic_trick()
            self.magic_locations.append(self.runs[self.run].actors[self.params['magic']['actor']].actor.get_actor_location())
            if (self.magic_locations[self.run] != self.magic_locations[self.run - 1]):
                ue.log("Magic locations don't match")
                self.runs[self.run].del_actors()
                self.runs[self.run].is_valid = False

    def generate_magic_runs(self, scene_index):
        if (self.is_occluded is False and 'O2' in type(self).__name__):
            magic_tick = 50
        magic_tick = math.ceil((self.params['magic']['tick'] + 1) / 2)
        ue.log("magic tick = {}".format(magic_tick))
        # TODO make the same thing for the status.json
        # removing the run subdirectory from the path
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

    def is_possible(self):
        return True if self.run_index - self.get_nchecks() in (3, 4) else False
