import random
import unreal_engine as ue
from scenario.scene import Scene
from unreal_engine import FVector, FRotator
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material
from actors.object import Object


class Test(Scene):
    def __init__(self, world, saver, is_occluded, movement):
        self.is_occluded = is_occluded
        self.movement = movement
        self.check_array = {}
        self.ticker = 0
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()
        # random number of object
        nobjects = random.randint(1, 3)
        # TODO remove
        nobjects = 3
        # random number of occluder if it's not dynamic 2
        # TODO implement it
        noccluders = random.randint(1 if '2' not in self.movement else 2, 2)
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
            if 'static' in self.movement:
                # if static, no initial force and differents initial locations
                # left, middle and right of the screen
                location = FVector(1000, (n - 1) * (500 + (scale * 50)), 0)
                force = FVector(0, 0, 0)
            else:
                # if dynamic, initial force and differents initial locations
                # they are more and more far. The more far they are,
                # the more they are far from the center of the screen
                location = FVector(1000 + (50 + (scale * 50)) * n,
                                   (1500 + 250 * (n - 1)) *
                                   (-1 if bool(random.getrandbits(1))
                                   else 1), 0)
                # the more far they are, the more force we apply on them
                # an object has one chance out of two to fly
                force = FVector(0, (4e4 + abs(location.y - 1500) * 10) *
                                (-1 if location.y > 0 else 1),
                                1e6 if bool(random.getrandbits(1)) else 0)
                # if an object is not a sphere, it will necessarly fly
                if self.params[object_names[n]].mesh != 'Sphere':
                    force.z = 3e4 + (location.y - 1500) * 5
                # if at least on object will fly,
                # the occluder needs to be higher
                if force.z != 0:
                    occluder_scale.z = 1.95
            self.params[object_names[n]].location = location
            self.params[object_names[n]].initial_force = force
        # random magic object
        self.params['magic'] = {
            'actor': 'object_{}'.format(random.randint(1, nobjects)),
            'tick': -1}
        # array that will contain occluders name
        occluder_names = []
        # TODO remove once it is implemented
        noccluders = 1
        if self.is_occluded:
            for n in range(noccluders):
                self.params['occluder_{}'.format(n)] = OccluderParams()
                self.params['occluder_{}'.format(n)].scale = occluder_scale
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
                self.params[random.choice(occluder_names)].location = \
                    FVector(600,
                            self.params[self.params['magic']['actor']].location.y / 2 + (50 * occluder_scale.x * (-1 if self.params[self.params['magic']['actor']].location.y < 0 else 1)),
                            0)

    def play_run(self):
        super().play_run()
        self.ticker = 0
        self.setup_magic_actor()

    def tick(self):
        super().tick()
        if self.ticker == 60 or self.ticker == 70 or self.ticker == 80:
            # print(self.actors[self.params['magic']['actor']].initial_force)
            for name, actor in self.actors.items():
                if ('object' in name and
                        int(round(actor.actor.get_actor_velocity().y)) == 0):
                    actor.set_force(actor.initial_force)
                    break
        self.ticker += 1

    def checks_time_laps(self, check_array, desired_bool):
        # check_array can either be an
        # array of both runs or an array of one run
        # we are looking for the desired bool in this/these array(s)
        res = []
        if len(check_array) == 2:
            if len(check_array[0]) == len(check_array[1]):
                nb = len(check_array[0])
            else:
                ue.log_warning("run's arrays size don't match")
                return res
        else:
            nb = len(check_array)
        for frame in range(nb):
            if (len(check_array) == 2 and check_array[0][frame] ==
                    check_array[1][frame] and
                    check_array[1][frame] == desired_bool):
                res.append(frame)
            elif len(check_array) > 2 and check_array[frame] == desired_bool:
                res.append(frame)
        return res

    def magic_actor(self):
        return self.actors[self.params['magic']['actor']]

    def capture(self):
        ignored_actors = []
        if self.actors[self.params['magic']['actor']].hidden is True:
            ignored_actors.append(self.actors[self.params['magic']['actor']]
                                  .actor)
        self.saver.capture(ignored_actors, self.status_header,
                           self.get_status())

    def set_magic_tick(self):
        if self.is_occluded is True:
            if 'static' in self.movement:
                return self.static_occluded()
            elif 'dynamic_1' in self.movement:
                return self.dynamic_1_occluded()
            else:
                return self.dynamic_2_occluded()
        else:
            if 'static' in self.movement:
                return self.static_visible()
            elif 'dynamic_1' in self.movement:
                return self.dynamic_1_visible()
            else:
                return self.dynamic_2_visible()
