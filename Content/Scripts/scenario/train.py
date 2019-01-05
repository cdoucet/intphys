import random
import math
from scenario.scene import Scene
from unreal_engine import FVector, FRotator
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
import unreal_engine as ue
from actors.object import Object

class Train(Scene):
    def __init__(self, world, saver):
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()
        nobjects = random.randint(1, 3)
        for n in range(nobjects):
            force = FVector()
            vforce = []
            for i in range(3):
                vforce.append(random.choice([-4, -3, -2, 2, 3, 4]))
                vforce.append(random.uniform(3, 4))
            # the vertical force is necessarly positive
            vforce[4] = abs(vforce[4])
            force = FVector(vforce[0] * math.pow(10, vforce[1]),
                            vforce[2] * math.pow(10, vforce[3]),
                            vforce[4] * math.pow(10, vforce[5]))
            # scale in [1.5, 2]
            scale = 1.5 + random.random() * 0.5
            location = FVector(
                    random.uniform(200, 700),
                    random.uniform(-500, 500),
                    0)
            rotation = FRotator(
                0, 0, 360*random.random())
            mesh = random.choice([m for m in Object.shape.keys()])
            self.params['object_{}'.format(n+1)] = ObjectParams(
                mesh=mesh,
                material=get_random_material('Object'),
                location=location,
                rotation=rotation,
                scale=FVector(scale, scale, scale),
                mass=1,
                initial_force=force)
            noccluders = random.randint(0, 4)
            self.is_occluded = True if noccluders != 0 else False
        for n in range(noccluders):
            location = FVector(
                    random.uniform(200, 700),
                    random.uniform(-500, 500),
                    0)
            rotation = FRotator(
                    0, 0, random.uniform(-180, 180))
            nmoves = random.randint(0, 3)
            moves = []
            for m in range(nmoves):
                if len(moves) == 0:
                    moves.append(random.randint(0, 200))
                else:
                    moves.append(random.randint(moves[-1], 200))
            self.params['occluder_{}'.format(n+1)] = OccluderParams(
                material=get_random_material('Wall'),
                location=location,
                rotation=rotation,
                scale=FVector(random.uniform(0.5, 1.5), 1, random.uniform(0.5, 1.5)),
                moves=moves,
                speed=random.uniform(1, 5),
                warning=True,
                start_up=random.choice([True, False]))

    def stop_run(self, scene_index, total):
        super().stop_run()
        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index, total))
            # reset actors if it is the last run
            self.saver.reset(True)
        self.del_actors()
        self.run += 1

    def play_run(self):
        if self.run == 1:
            return
        # ue.log("Run 1/1: Possible run")
        super().play_run()
        for name, actor in self.actors.items():
            if 'object' in name.lower() and random.choice([0, 1, 2]) != 0:
                actor.set_force(actor.initial_force)

    def is_possible(self):
        return True

    def is_test_scene(self):
        return False

    def capture(self):
        ignored_actors = []
        self.saver.capture(ignored_actors, self.get_status())

    def is_over(self):
        return True if self.run == 1 else False
