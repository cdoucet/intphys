import random

from unreal_engine import FVector, FRotator
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from scenario.run import RunImpossible
from unreal_engine.classes import ScreenshotManager


class SandBoxBase:
    def __init__(self, world, saver=None, is_occluded=None, movement=None):
        super().__init__(world, saver)
        self.generate_parameters()
        for run in range(1):
            self.runs.append(RunImpossible(self.world, self.params))

    @property
    def name(self):
        return 'SandBox'

    def tick(self, tick_index):
        super().tick(tick_index)
        ignored_actors = []
        magic_actor = None
        for actor_name, actor in self.runs[0].actors.items():
            if 'object' not in actor_name.lower() and 'occluder' not in actor_name.lower():
                if 'walls' in actor_name.lower():
                    ignored_actors.append(actor.front.actor)
                    ignored_actors.append(actor.left.actor)
                    ignored_actors.append(actor.right.actor)
                else:
                    ignored_actors.append(actor.actor)
            else:
                if 'object' in actor_name.lower():
                    magic_actor = actor.actor
        # print(tick_index)
        res = ScreenshotManager.IsActorInLastFrame(magic_actor, [])[0]
        print(res)

class SandBoxTrain(SandBoxBase, Scene):
    def generate_parameters(self):
        super().generate_parameters()
        self.params[f'object_{1}'] = ObjectParams(
                mesh='Cube',
                material=get_random_material('Object'),
                location=FVector(500, 0, 0),
                rotation=FRotator(0, 0, 45),
                scale=FVector(1, 1, 1),
                mass=100,
                force=FVector(0, 0, 0))
        self.params['occluder'] = OccluderParams(
                material=get_random_material('Wall'),
                location=FVector(400, 0, 0),
                rotation=FRotator(0, 0, 90),
                scale=FVector(1, 1, 1),
                moves=[0],
                start_up=True,
                speed=1)
    
    def play_run(self):
        super().play_run()


class SandBoxTest(SandBoxBase, Scene):
    pass
