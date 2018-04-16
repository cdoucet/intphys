import random

from unreal_engine import FVector, FRotator
from unreal_engine.classes import ScreenshotManager
from scenario import base_scenario
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material


class O1Base(object):
    @property
    def name(self):
        return 'O1'


class O1Train(O1Base, base_scenario.BaseTrain):
    def random_location(self, index, side=None):
        if side is None:
            side = 'left' if random.random() < 0.5 else 'right'

        return FVector(
            550 + 150 * float(index - 1),
            -500 if side == 'left' else 500,
            70 + 200 * random.random())

    def generate_parameters(self):
        params = super().generate_parameters()

        nobjects = 1  # random.randint(1, 3)
        for n in range(1, nobjects + 1):
            scale = 1.5 + random.random()
            params[f'object_{n}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=FVector(2000, 0, 0),  # self.random_location(n),
                rotation=FRotator(0, 0, 0),
                scale=FVector(scale, scale, scale),
                mass=100)

        return params


class O1TestStatic(O1Base, base_scenario.BaseTest):
    is_magic_actor_hidden = False
    is_valid = True
    is_actor_in_frame = []
    def get_nchecks(self):
        return 1 if self.is_occluded else 0

    def generate_parameters(self):
        params = super().generate_parameters()
        locations = [FVector(1000, 500 * y, 0) for y in (-1, 0, 1)]
        random.shuffle(locations)

        nobjects = random.randint(1, 3)
        for n in range(nobjects):
            # scale in [1, 1.5]
            scale = 1 + random.random() * 0.5

            # full random rotation (does not matter on spheres, except
            # for texture variations)
            rotation = FRotator(
                360*random.random(), 360*random.random(), 360*random.random())

            params[f'object_{n+1}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=locations[n],
                rotation=rotation,
                scale=FVector(scale, scale, scale),
                mass=100)

 
        params['magic'] = {
            'actor': f'object_{random.randint(1, nobjects)}',
            'tick': random.randint(10, 90)}
        if self.is_occluded:
            params['occluder'] = OccluderParams(
                material=get_random_material('Wall'),
                location=FVector(400, params[params['magic']['actor']].location.y / 2, 0),
                rotation=FRotator(0, 0, 90),
                scale=FVector(1, 1, 1),
                moves=[0, 90],
                speed=1,
                start_up=False)

        return params

    def setup_magic_trick(self, actor, run):
        if run in (2, 4):
            self.is_magic_actor_hidden = True
            actor.set_hidden(False)
    def apply_magic_trick(self, actor, run):
        if run <= 2:
            actor.set_hidden(not actor.hidden)
            if (self.is_occluded):
                self.is_valid = not ScreenshotManager.IsActorInLastFrame(actor.actor, [])
            self.is_magic_actor_hidden = actor.hidden

    def run_tick_check(self, magic_actor):
        self.is_actor_in_frame.append(ScreenshotManager.IsActorInLastFrame(magic_actor.get_actor()))

    def run_check(self):
        try:
            return self.is_actor_in_frame.index(False)
        except ValueError:
            return -1
