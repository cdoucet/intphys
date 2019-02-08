import random
import math
from scenario.mirrorTest import MirrorTest
from scenario.scene import Scene
from scenario.train import Train
from scenario.test import Test
from unreal_engine import FVector, FRotator
from unreal_engine.classes import ScreenshotManager
from scenario.checkUtils import checks_time_laps
from scenario.checkUtils import remove_last_and_first_frames
from scenario.checkUtils import remove_invisible_frames
from scenario.checkUtils import separate_period_of_occlusions
from scenario.checkUtils import store_actors_locations
from scenario.checkUtils import remove_frames_close_to_magic_tick
from actors.parameters import OccluderParams
from tools.materials import get_random_material

class O3Base:
    @property
    def name(self):
        return 'O3'

    @property
    def description(self):
        return 'Spatio-temporal continuity'


class O3Train(O3Base, Train):
    pass


class O3Test(O3Base, MirrorTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]

    def generate_parameters(self):
        super().generate_parameters()
        self.params['Floor'].restitution = 1
        self.params['Floor'].friction = 0
        if self.is_occluded is True:
            if '2' in self.movement:
                self.params['occluder_3'] = OccluderParams()
                self.params['occluder_4'] = OccluderParams()
            elif '1' in self.movement:
                # self.params['Camera'].location.x -= 200
                self.params['occluder_2'] = OccluderParams()
                self.params['occluder_1'].location = \
                    FVector(600,
                            250,
                            0)
                self.params['occluder_2'].location = \
                    FVector(600,
                            -250,
                            0)
        for name, params in self.params.items():
            if 'ccluder' in name:
                params.rotation = FRotator(0, 0, 90)
                params.material = get_random_material('Wall')
                params.start_up = False
                params.moves = [0, 125]
                if 'dynamic_1' in self.movement:
                    params.speed = 2
                    params.moves[0] = random.randint(0, 10)
                    params.moves[1] = random.randint(150, 160)
                    params.scale.x = 0.6
                    params.scale.z = 2.7
                elif 'dynamic_2' in self.movement:
                    # occluder x size -> 400
                    params.speed = 2
                    params.moves[0] = random.randint(0, 10)
                    params.moves[1] = random.randint(150, 160)
                    params.location = FVector()
                    params.location.x = 600
                    params.scale = FVector((params.location.x * 2 / 9) / 400, 1, 2)
                    params.location.y = (400 * params.scale.x * int(name[-1]) * 2) - params.location.x - (400 * params.scale.x / 2)
                    if self.params['Camera'].location.y == params.location.y:
                        raise ValueError('the camera is on the same y axes than an occluder')
                # else:
                    # TODO ask if it is ok to have occluders not straights
                    # params.location.x = 500
                    # params.rotation.yaw += math.degrees(math.atan((params.location.y - (50 * params.scale.x * (-1 if params.location.y < 0 else 1))) / params.location.x))
            elif 'bject' in name:
                params.restitution = 1
                params.friction = 0
                if 'dynamic_1' in self.movement:
                    params.initial_force.z = 3e4 + (abs(params.location.y) - 1500) * 4
                elif 'dynamic_2' in self.movement:

                    n = round((params.location.x - 1000) / (params.scale.x * 100 * math.sqrt(3)), 0)
                    if n == 0:
                        scale = random.uniform(0.7, 0.9)
                    elif n == 1:
                        scale = random.uniform(0.9, 1.1)
                    elif n == 2:
                        scale = random.uniform(1.1, 1.3)
                    # print(f"n = {round((params.location.x - 1000) / (params.scale.x * 100 * math.sqrt(3)), 0)} | location = {params.location}")
                    params.scale = FVector(scale, scale, scale)
                    params.initial_force = FVector(0, (4e4 + (abs(params.location.y) - 1500) * 10) * (-1 if params.location.y > 0 else 1), 2e4)
                    params.initial_force.z *= random.uniform(0.85, 1)
                params.mesh = 'Sphere'


    def tick(self):
        if 'dynamic' in self.movement and self.is_occluded is True:
            Scene.tick(self)
            if self.ticker == 40 or self.ticker == 50 or self.ticker == 60:
                # print(self.actors[self.params['magic']['actor']].initial_force)
                max_name = ""
                # it just must be a very very big value
                max_x = 10000000
                for name, actor in self.actors.items():
                    if ('object' in name and
                            int(round(actor.actor.get_actor_velocity().y)) == 0 and
                            int(round(actor.actor.get_actor_velocity().z)) == 0):
                        if actor.actor.get_actor_location().x < max_x:
                            max_x = actor.actor.get_actor_location().x
                            max_name = name
                if max_x != 10000000:
                    self.actors[max_name].set_force(self.actors[max_name].
                                                    initial_force)
            self.ticker += 1
        else:
            super().tick()

    # We avoid comparing the locations of the magic actor during magic tick
    def set_magic_tick(self):
        if (Test.set_magic_tick(self) is False):
            return False

    def setup_magic_actor(self):
        actor_max_scale = 0
        for name, actor in self.actors.items():
            if 'bject' in name and actor.scale.x > actor_max_scale:
                actor_max_scale = actor.scale.x
        if self.run == 1:
            magic_actor = self.actors[self.params['magic']['actor']]
            current_location = magic_actor.actor.get_actor_location()
            length = 0
            target_location = FVector(0, 0, 0)
            if self.is_occluded is False and 'static' not in self.movement:
                length = random.uniform(400, 600)
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            elif 'static' in self.movement:
                length = random.uniform(400, 600)
                target_location = FVector(current_location.x + length,
                                          current_location.y,
                                          current_location.z)
            elif '1' in self.movement:
                # thales theorem
                if magic_actor.actor.get_actor_location().y > 0:
                    length = 250 * (self.actors[self.params['magic']['actor']].location.x) / self.actors['occluder_1'].location.y
                else:
                    length = -1 * 250 * (self.actors[self.params['magic']['actor']].location.x) / self.actors['occluder_1'].location.y
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            else:
                # print("previous location = {}".format(magic_actor.actor.get_actor_location()))
                # thales theorem
                if magic_actor.actor.get_actor_location().y > 0:
                    length = -1 * 133.3333 * (self.actors[self.params['magic']['actor']].location.x) / self.actors['occluder_1'].location.y
                else:
                    length = 133.3333 * (self.actors[self.params['magic']['actor']].location.x) / self.actors['occluder_1'].location.y
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
                #print("jump = {}".format(length))
                #print("new location = {}".format(target_location))
            magic_actor.set_location(target_location)

    # this function is here so you can put only the attribute that please you
    # in the check array. It is called every tick
    # there is two dictionaries : one for each run
    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        location = store_actors_locations(self.actors)
        self.check_array['location'][self.run].append(location)
        frame = (self.ticker / 2) - 0.5
        IsActorInFrame = ScreenshotManager.IsActorInFrame(magic_actor, frame)
        self.check_array['visibility'][self.run].append(IsActorInFrame)

    def static_visible(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 5)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        visibility_array = \
            remove_frames_close_to_magic_tick(visibility_array,
                                              self.params['magic']['tick'][0],
                                              5)
        self.params['magic']['tick'].append(random.choice(visibility_array))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = checks_time_laps(self.check_array["visibility"], False)
        visibility_array = remove_invisible_frames(visibility_array)
        # We need to separate occlusions because in the O3 bloc,
        # The objects are not at the same place at each run
        occlusion = separate_period_of_occlusions(visibility_array)
        self.params['magic']['tick'] = occlusion[1][int(len(occlusion[1]) / 2)]
        return True

    def dynamic_2_occluded(self):
        if self.check_array["visibility"][0][0] or self.check_array["visibility"][1][0]:
            print('magic object visible at first tick')
            return False
        visibility_array_temp = []
        visibility_array_temp.append(checks_time_laps(self.check_array["visibility"][0], False))
        visibility_array_temp.append(checks_time_laps(self.check_array["visibility"][1], False))
        # visibility_array = checks_time_laps(self.check_array["visibility"], False)
        visibility_array_temp[0] = remove_invisible_frames(visibility_array_temp[0])
        visibility_array_temp[1] = remove_invisible_frames(visibility_array_temp[1])
        visibility_array = []
        #print(visibility_array_temp)
        i = 0
        j = 0
        while True:
            if visibility_array_temp[0][i] == visibility_array_temp[1][j]:
                visibility_array.append(visibility_array_temp[0][i])
                i += 1
                j += 1
            elif visibility_array_temp[0][i] < visibility_array_temp[1][j]:
                i += 1
            elif visibility_array_temp[0][i] > visibility_array_temp[1][j]:
                j += 1
            if i >= len(visibility_array_temp[0]) or j >= len(visibility_array_temp[1]):
                break
        #print(visibility_array)
        occlusion = separate_period_of_occlusions(visibility_array)
        #print(occlusion)
        if len(occlusion) < 2:
            print("Not enough occlusion period")
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(occlusion[0][int(len(occlusion[1]) / 2)])
        self.params['magic']['tick'].append(occlusion[-1][int(len(occlusion[-1]) / 2)])
        return True
