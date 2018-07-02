"""Block SandBox is apparition/disparition, spheres only"""
import random
import math
from unreal_engine import FVector, FRotator
from scenario.train import Train
from scenario.scene import Scene
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from actors.object import Object
import unreal_engine as ue
from scenario.mirrorTest import MirrorTest
from scenario.O1 import O1Test


class SandBoxBase:
    @property
    def name(self):
        return 'SandBox'

    @property
    def description(self):
        return 'bloc SandBox'


class SandBoxTrain(SandBoxBase, Train):
    pass


class SandBoxTest(SandBoxBase, O1Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, False, "dynamic_1")

    def generate_parameters(self):
        MirrorTest.generate_parameters(self)
        # random number of object
        nobjects = random.randint(1, 3)
        nobjects = 3
        # random number of occluder if it's not dynamic 2
        # TODO implement random number of occluders
        noccluders = 1 if '2' not in self.movement else 2
        # occluder scale
        occluder_scale = FVector(0.5, 1, 1)
        # array that will contains object names
        object_names = []
        for n in range(3):
            object_names.append('object_{}'.format(n+1))
        # shuffle names to make that the "object_1" is
        # not always the closest one on the screen
        random.shuffle(object_names)
        for n in range(3):
            self.params[object_names[n]] = ObjectParams()
            # random scale between [1, 1.5]
            scale = 2 + random.uniform(0, 0.5)
            self.params[object_names[n]].scale = FVector(scale, scale, scale)
            self.params[object_names[n]].mass = 1
            # full random yaw rotation (z axis)
            # (does not matter on spheres, except for texture variations)
            self.params[object_names[n]].rotation = \
                FRotator(0, 0, 360*random.random())
            # random mesh
            self.params[object_names[n]].mesh = random.choice(
                [m for m in Object.shape.keys()])
            self.params[object_names[n]].mesh = "Cube"
            # random material
            self.params[object_names[n]].material = \
                get_random_material('Object')
            if 'static' in self.movement:
                # if static, no initial force and differents initial locations
                # left, middle and right of the screen
                location = FVector(1000, (n - 1) * (500 + (scale * 50)), 0)
                force = FVector(0, 0, 0)
            else:
                """
                if dynamic, there is an initial force and differents initial locations
                the x axis:
                  the closest object is located at 1000 from the camera
                  the second object is more far, calculated from the diagonal of a cube mesh
                  (to be sure mesh won't collide)
                  same for the third object
                the y axis:
                  they need to be off the screen at first frame, so we put it at 1000 from the center
                  then we offset the second object (and the third one) because the ifeld of view of the camera is an angle
                  then we offset again every object calculated from the diagonal of a cube mesh
                  (to be sure mesh won't collide)
                  then we offset them a last time to be sure their shadows won't be visible
                """
                location = FVector(1000 +
                                   scale * 100 * math.sqrt(3) * n,
                                   1000 + abs(self.params['Camera'].location.x)
                                   + scale * 100 * math.sqrt(3) * n
                                   + scale * 100 * math.sqrt(3) * (n + 1),
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
                # if at least on object will fly,
                # the occluder needs to be higher
                # if object is too big, make occluder bigger
                if scale / 2 > occluder_scale.x:
                    occluder_scale.x = scale / 2
                if force.z != 0:
                    occluder_scale.z = 1.5
            self.params[object_names[n]].location = location
            self.params[object_names[n]].initial_force = force
        # remove object if there should not be 3 objects on the scene
        # because we created three objects
        if nobjects <= 2:
            del self.params['object_3']
            # remove if there should not be 2 objects on the scene
            if nobjects == 1:
                del self.params['object_2']
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
                self.params['occluder_{}'.format(n)].moves = [0, 100]
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

