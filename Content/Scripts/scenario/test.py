import random
import math
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

    def play_run(self):
        super().play_run()
        self.ticker = 0
        self.setup_magic_actor()

    def tick(self):
        super().tick()
        if self.ticker == 60 or self.ticker == 70 or self.ticker == 80:
            # print(self.actors[self.params['magic']['actor']].initial_force)
            max_name = ""
            # it just must be a very very big value
            max_x = 10000000
            for name, actor in self.actors.items():
                if ('object' in name and
                        int(round(actor.actor.get_actor_velocity().y)) == 0):
                    if actor.actor.get_actor_location().x < max_x:
                        max_x = actor.actor.get_actor_location().x
                        max_name = name
            if max_x != 10000000:
                self.actors[max_name].set_force(self.actors[max_name].
                                                initial_force)
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
        if ('dynamic' in self.movement and
                (self.check_array['visibility'][0][0] == 1 or
                 self.check_array['visibility'][1][0] == 1)):
            ue.log_warning("object is not invisible at first tick")
            return False
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
