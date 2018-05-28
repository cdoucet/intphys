"""Block SandBox is apparition/disparition, spheres only"""
import random
from unreal_engine import FVector, FRotator
from scenario.fullTest import FullTest
from scenario.train import Train
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
# import unreal_engine as ue


class SandBoxBase:
    @property
    def name(self):
        return 'SandBox'

    @property
    def description(self):
        return 'bloc SandBox'


class SandBoxTrain(SandBoxBase, Train):
    pass


class SandBoxTest(SandBoxBase, FullTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, True, "dynamic_1")

    def generate_parameters(self):
        Scene.generate_parameters(self)
        nobjects = 2
        if 'static' in self.movement:
            locations = [FVector(1000, 500 * y, 0) for y in (-1, 0, 1)]
        else:
            # random side for each actor: starting either from left
            # (go to right) or from rigth (go to left)
            locations = [FVector(1000 + 300 * y, -1250, 0)
                         for y in (-1, 0, 1)]
            locations[1].y += 200 if locations[1].y > 0 else -200
            locations[2].y += 350 if locations[2].y > 0 else -350
        # random.shuffle(locations)
        for n in range(nobjects):
            # scale in [1, 1.5]
            scale = 2
            initial_force = FVector(0, 0, 0)
            if 'static' not in self.movement:
                locations[n].x = locations[n].x + 50 * scale
                initial_force = FVector(0, -25e6 if locations[n].y > 0
                                        else 25e6, 0)
                # initial_force.z = 14e6
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
                mass=1,
                initial_force=initial_force)
        self.params['magic'] = {
            'actor': 'object_2',
            'tick': -1}
        if self.is_occluded:
            moves = []
            scale = FVector(0.5, 1, 2.7)
            if 'dynamic' in self.movement:
                if '2' in self.movement:
                    location = FVector(600, -175, 0)
                else:
                    location = FVector(600, 0, 0)
                    scale.x = 1
                start_up = False
                moves.append(0)
                moves.append(110)
            else:
                location = FVector(600, self.params[
                    self.params['magic']['actor']].location.y / 2, 0)
                scale.z = 1.5
                scale.x = 1
                start_up = False
                moves.append(0)
                moves.append(110)
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

    def setup_magic_actor(self):
        pass

    def play_magic_trick(self):
        magic = self.actors[self.params['magic']['actor']]
        magic.reset_force()
        magic.set_force(FVector(0, magic.initial_force.y * -1, 0))

    def fill_check_array(self):
        self.params['magic']['tick'] = 120

    def set_magic_tick(self):
        pass

    def tick(self):
        Scene.tick(self)
        if self.run <= 1:
            self.fill_check_array()
        elif isinstance(self.params['magic']['tick'], int) and \
                self.ticker == self.params['magic']['tick']:
            self.play_magic_trick()
        elif not isinstance(self.params['magic']['tick'], int) and \
                self.ticker in self.params['magic']['tick']:
            self.play_magic_trick()
        if self.ticker == 80 or self.ticker == 90 or self.ticker == 100:
            # print(self.actors[self.params['magic']['actor']].initial_force)
            for name, actor in self.actors.items():
                if 'object' in name and int(round(actor.actor.
                                            get_actor_velocity().y)) == 0:
                    actor.set_force(actor.initial_force)
                    break
        self.ticker += 1
