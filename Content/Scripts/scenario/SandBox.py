"""Block SandBox is apparition/disparition, spheres only"""
import random
import math
from unreal_engine.classes import ScreenshotManager
from unreal_engine.classes import Friction
from unreal_engine import FVector, FRotator
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from scenario.test import Test
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from actors.object import Object
import unreal_engine as ue
from scenario.O3 import O3Test


class SandBoxBase:
    @property
    def name(self):
        return 'SandBox'

    @property
    def description(self):
        return 'bloc SandBox'


class SandBoxTrain(SandBoxBase, Train):
    pass


class SandBoxTest(SandBoxBase, O3Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, True, "dynamic_1")

    def generate_parameters(self):
        Scene.generate_parameters(self)
        if '2' in self.movement and self.is_occluded is True:
            self.params['Camera'].location.x -= 300
            self.params['Floor'].location.x -= 300
        # random number of object
        nobjects = random.randint(1, 3)
        # TODO remove
        nobjects = 3
        # random number of occluder if it's not dynamic 2
        # TODO implement random number of occluders
        noccluders = 1 if '2' not in self.movement else 2
        # occluder scale
        occluder_scale = FVector(0.5, 1, 1)
        # array that will contains object names
        object_names = []
        for n in range(nobjects):
            object_names.append('object_{}'.format(n+1))
        # shuffle names to make that the "object_1" is
        # not always the closest one on the screen
        random.shuffle(object_names)
        for n in range(nobjects):
            self.params[object_names[n]] = ObjectParams()
            # random scale between [1.5, 2]
            scale = 1.5 + random.uniform(0, 0.5)
            # if object is too big, make occluder bigger
            if scale - 1.35 > occluder_scale.x:
                occluder_scale.x = scale - 1.35
            self.params[object_names[n]].scale = FVector(scale, scale, scale)
            self.params[object_names[n]].mass = 1
            # full random yaw rotation (z axis)
            # (does not matter on spheres, except for texture variations)
            self.params[object_names[n]].rotation = \
                FRotator(0, 0, 360*random.random())
            # random mesh
            self.params[object_names[n]].mesh = random.choice(
                [m for m in Object.shape.keys()])
            # random material
            self.params[object_names[n]].material = \
                get_random_material('Object')
            self.params[object_names[n]].mesh = "Sphere"
            if 'static' in self.movement:
                # if static, no initial force and differents initial locations
                # left, middle and right of the screen
                location = FVector(1000, (n - 1) * (500 + (scale * 50)), 0)
                force = FVector(0, 0, 0)
            else:
                # if dynamic, initial force and differents initial locations
                # they are more and more far. The more far they are,
                # the more they are far from the center of the screen
                # Plus, the y location depends on the camera x location
                location = FVector(1000 + scale * 100 * math.sqrt(3) * n,
                                   1000 + abs(self.params['Camera'].location.x) +
                                   scale * 100 * math.sqrt(3) * n
                                   + scale * 100 * math.sqrt(2),
                                   0)
                if random.choice([0, 1]) == 1:
                    location.y *= -1
                # the more far they are, the more force we apply on them
                # an object has one chance out of two to fly
                force = FVector(0, (4e4 + (abs(location.y) - 1500) * 10) *
                                (-1 if location.y > 0 else 1),
                                3e4 + (abs(location.y) - 1500) * 4)
                # if an object is not a sphere, it will necessarly fly
                if self.params[object_names[n]].mesh != 'Sphere':
                    force.z = 3e4 + (abs(location.y) - 1500) * 4
                force.z = 0
                # force.z = 0
                # if at least on object will fly,
                # the occluder needs to be higher
                if force.z != 0:
                    occluder_scale.z = 2.5
            self.params[object_names[n]].location = location
            self.params[object_names[n]].initial_force = force
        # random magic object
        self.params['magic'] = {
            'actor': 'object_{}'.format(random.randint(1, nobjects)),
            'tick': -1}
        # array that will contain occluders name
        occluder_names = []
        # TODO remove once it is implemented
        if self.is_occluded:
            for n in range(noccluders):
                self.params['occluder_{}'.format(n)] = OccluderParams()
                self.params['occluder_{}'.format(n)].scale = occluder_scale
                self.params['occluder_{}'.format(n)].material = \
                    get_random_material('Wall')
                # the occluder start down
                self.params['occluder_{}'.format(n)].start_up = False
                self.params['occluder_{}'.format(n)].rotation = \
                    FRotator(0, 0, 90)
                self.params['occluder_{}'.format(n)].location = \
                    FVector(500, 0, 0)
                #   FVector(800, (n - 1) * (500 + (occluder_scale.x * 200)), 0)
                # the occluder will rise at first frame and at the 100th one
                self.params['occluder_{}'.format(n)].moves = [0, 120]
                occluder_names.append('occluder_{}'.format(n))
            # if static, a random occluder will go between the magic
            # actor and the occluder
            if 'static' in self.movement:
                first = random.choice(occluder_names)
                occluder_names.remove(first)
                magic_location_y = \
                    self.params[self.params['magic']['actor']].location.y
                self.params[first].location = \
                    FVector(600,
                            magic_location_y / 2 + (50 * occluder_scale.x *
                                                    (-1 if magic_location_y < 0
                                                        else 1)),
                            0)
            if len(occluder_names) == 2:
                self.params[occluder_names[0]].location = \
                    FVector(600,
                            200,
                            0)
                self.params[occluder_names[1]].location = \
                    FVector(600,
                            -200,
                            0)

        # O3
        max_name = ""
        max_x = 10000000
        for name, actor in self.params.items():
            if ('object' in name):
                if actor.location.x < max_x:
                    max_x = actor.location.x
                    max_name = name
        self.params['magic']['actor'] = max_name
        self.params
        for name, params in self.params.items():
            if 'ccluder' in name:
                if 'dynamic_1' in self.movement:
                    params.scale.x = 1.5
                elif 'dynamic_2' in self.movement:
                    params.scale.x = 1
                    params.location.y += 130 * (1 if params.location.y > 0
                                                else -1)
            elif name == self.params['magic']['actor']:
                pass
            elif 'bject' in name:
                pass

    def setup_magic_actor(self):
        if self.run == 1:
            magic_actor = self.actors[self.params['magic']['actor']]
            current_location = magic_actor.actor.get_actor_location()
            length = 0
            target_location = FVector(0, 0, 0)
            if 'static' in self.movement:
                length = random.randint(300, 500)
                length = 500
                target_location = FVector(current_location.x + length,
                                          current_location.y,
                                          current_location.z)
            elif '1' in self.movement:
                if magic_actor.actor.get_actor_location().y > 0:
                    length = random.randint(300, 500)
                    length = 800
                else:
                    length = random.randint(-500, -300)
                    length = -800
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            else:
                if magic_actor.actor.get_actor_location().y > 0:
                    length = random.randint(200, 250)
                    length = 350
                else:
                    length = random.randint(-250, -200)
                    length = -350
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            ue.log("jump length = {}".format(length))
            magic_actor.set_location(target_location)

    def set_magic_tick(self):
        self.params['magic']['tick'] = 56
