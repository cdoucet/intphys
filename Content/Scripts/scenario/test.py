import random

import unreal_engine as ue
from scenario.scene import Scene
from scenario.run import RunCheck, RunPossible, RunImpossible
from unreal_engine import FVector, FRotator
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material


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
        for run in range(2):
            self.runs.append(RunImpossible(self.world, self.saver, self.params,
                {
                    'name': self.name,
                    'type': 'test',
                    'is_possible': False}
                ))
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
            side_bool = bool(random.getrandbits(1))
            self.side = 'left' if side_bool is True else 'right'
            locations = [FVector(1000 + 200 * y, -500 if 'left' in self.side else 500, 0) for y in (-1, 0, 1)]
        random.shuffle(locations)
        for n in range(nobjects):
            # scale in [1, 1.5]
            scale = 1 + random.random() * 0.5
            force = FVector(0, 0, 0)
            if 'static' not in self.movement:
                locations[n].x = locations[n].x + 50 * scale
            # full random rotation (does not matter on spheres, except
            # for texture variations)
            rotation = FRotator(
                360*random.random(), 360*random.random(), 360*random.random())
            self.params[f'object_{n+1}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=locations[n],
                rotation=rotation,
                scale=FVector(scale, scale, scale),
                mass=100)
        tick = -1 if self.is_occluded is True else 25
        self.params['magic'] = {
            'actor': f'object_{random.randint(1, nobjects)}',
            'tick': tick}
        if self.is_occluded:
            if 'dynamic' in self.movement:
                if self.movement.split('_')[1] == '2':
                    location = FVector(400, -250, 0)
                else:
                    location = FVector(400, 0, 0)
            else:
                location = FVector(400, self.params[self.params['magic']['actor']].location.y / 2, 0)
            self.params['occluder_1'] = OccluderParams(
                material=get_random_material('Wall'),
                location=location,
                rotation=FRotator(0, 0, 90),
                scale=FVector(1, 1, 1),
                moves=[0, 50],
                speed=2,
                start_up=False)
            if ('dynamic' in self.movement and self.movement.split('_')[1] == '2'):
                self.params['occluder_2'] = OccluderParams(
                    material=get_random_material('Wall'),
                    location=FVector(400, 250, 0),
                    rotation=FRotator(0, 0, 90),
                    scale=FVector(1, 1, 1),
                    moves=[0, 50],
                    speed=2,
                    start_up=False)

    def set_magic_tick(self, magic_tick):
        self.params['magic']['tick'] = magic_tick
        for run in self.runs:
            if (type(run) is RunImpossible):
                run.actors_params['magic']['tick'] = magic_tick

    def stop_run(self, scene_index):
        if (type(self.runs[self.run]) is RunCheck):
            self.set_magic_tick(self.runs[self.run].del_actors())
        else:
            self.runs[self.run].del_actors()
        super().stop_run(scene_index)

    def tick(self, tick_index):
        super().tick(tick_index)
        if tick_index % 100 == 1 and 'dynamic' in self.movement:
            for name, actor in self.runs[self.run].actors.items():
                if 'object' in name.lower():
                    actor.set_force(FVector(0, -1e9 if 'right' in self.side else 1e9, 7e8))
        if tick_index % 100 == self.params['magic']['tick'] and type(self.runs[self.run]) is RunImpossible:
            ue.log("tick {}: magic trick".format(tick_index % 100))
            self.apply_magic_trick()

    def is_possible(self):
        return True if self.run_index - self.get_nchecks() in (3, 4) else False
