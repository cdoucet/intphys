import random

from scenario.scene import Scene
from scenario.run import RunPossible
from unreal_engine import FVector, FRotator
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material


class Train(Scene):
    def __init__(self, world, saver):
        super().__init__(world, saver)
        self.runs.append(RunPossible(self.world, self.params))

    def random_location(self, index, side=None):
        if side is None:
            side = 'left' if random.random() < 0.5 else 'right'
        return FVector(
            550 + 150 * float(index - 1),
            -500 if side == 'left' else 500,
            70 + 200 * random.random())

    def generate_parameters(self):
        super().generate_parameters()
        nobjects = random.randint(1, 3)
        for n in range(nobjects):
            # scale in [1, 1.5]
            scale = 1 + random.random() * 0.5
            # full random rotation (does not matter on spheres, except
            # for texture variations)
            location = FVector(
                    random.uniform(-500, 500),
                    random.uniform(-500, 500),
                    random.uniform(0, 200))
            rotation = FRotator(
                360*random.random(), 360*random.random(), 360*random.random())
            self.params[f'object_{n+1}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=location,
                rotation=rotation,
                scale=FVector(scale, scale, scale),
                mass=100)
        noccluders = random.randint(0, 2)
        for n in range(noccluders):
            location = FVector(
                    random.uniform(-500, 500),
                    random.uniform(-500, 500),
                    random.uniform(0, 200))
            rotation = FRotator(
                    0, 0, random.uniform(-180, 180))
            nmoves = random.randint(0, 3)
            moves = []
            for m in range(nmoves):
                if len(moves) == 0:
                    moves.append(random.randint(0, 100))
                else:
                    moves.append(random.randint(moves[-1], 100))
            self.params[f'occluder_{n+1}'] = OccluderParams(
                material=get_random_material('Wall'),
                location=location,
                rotation=rotation,
                scale=FVector(1, 1, 1),
                moves=moves,
                speed=1,
                start_up=False)

    def is_possible(self):
        return True
