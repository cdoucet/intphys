import random
import math
from scenario.fullTest import FullTest
from scenario.train import Train
from scenario.test import Test
from unreal_engine import FVector, FRotator
from unreal_engine.classes import ScreenshotManager
from tools.materials import get_random_material
from scenario.checkUtils import checks_time_laps
from scenario.checkUtils import remove_last_and_first_frames
from scenario.checkUtils import remove_invisible_frames
from scenario.checkUtils import separate_period_of_occlusions
from scenario.checkUtils import store_actors_locations
from scenario.checkUtils import remove_frames_close_to_magic_tick
from actors.parameters import ObjectParams, OccluderParams
import unreal_engine as ue


class O3Base:
    @property
    def name(self):
        return 'O3'

    @property
    def description(self):
        return 'Spatio-temporal continuity'


class O3Train(O3Base, Train):
    pass


class O3Test(O3Base, FullTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]

    def spawn_actors(self):
        super().spawn_actors()
        print('spawn')
        self.linear_equations = []
        self.linear_equations.append([(self.actors['Camera'].location.x - self.actors['occluder_1'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_1'].location.y), 0])
        self.linear_equations[-1][1] = (self.actors['Camera'].location.y * self.actors['occluder_1'].location.x - self.actors['occluder_1'].location.y * self.actors['Camera'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_1'].location.y)
        self.linear_equations.append([(self.actors['Camera'].location.x - self.actors['occluder_2'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_2'].location.y), 0])
        self.linear_equations[-1][1] = (self.actors['Camera'].location.y * self.actors['occluder_2'].location.x - self.actors['occluder_2'].location.y * self.actors['Camera'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_2'].location.y)
        self.linear_equations.append([(self.actors['Camera'].location.x - self.actors['occluder_3'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_3'].location.y), 0])
        self.linear_equations[-1][1] = (self.actors['Camera'].location.y * self.actors['occluder_3'].location.x - self.actors['occluder_3'].location.y * self.actors['Camera'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_3'].location.y)
        self.linear_equations.append([(self.actors['Camera'].location.x - self.actors['occluder_4'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_4'].location.y), 0])
        self.linear_equations[-1][1] = (self.actors['Camera'].location.y * self.actors['occluder_4'].location.x - self.actors['occluder_4'].location.y * self.actors['Camera'].location.x) / (self.actors['Camera'].location.y - self.actors['occluder_4'].location.y)

    def generate_parameters(self):
        super().generate_parameters()
        self.params['Camera'].location.x = 0
        self.params['Floor'].restitution = 1
        if self.is_occluded is True and '2' in self.movement:
            self.params['occluder_3'] = OccluderParams()
            self.params['occluder_4'] = OccluderParams()
            for name, actor in self.params.items():
                if 'occluder' in name:
                    # occluder x size -> 400
                    actor.location = FVector()
                    actor.location.x = 600
                    actor.scale = FVector((actor.location.x * 2 / 9) / 400, 1, 2)
                    actor.rotation = FRotator(0, 0, 90)
                    actor.material = get_random_material('Wall')
                    actor.start_up = False
                    actor.moves = [0, 125]
                    actor.location.y = (400 * actor.scale.x * int(name[-1]) * 2) - actor.location.x - (400 * actor.scale.x / 2)
                    if self.params['Camera'].location.y == actor.location.y:
                        raise ValueError('the camera is on the same y axes than an occluder')
                if 'object' in name:
                    actor.restitution = 1
                    actor.mesh = "Sphere"
                    actor.scale = FVector(1, 1, 1)
                    actor.initial_force = FVector(0, (4e4 + (abs(actor.location.y) - 1500) * 10) * (-1 if actor.location.y > 0 else 1), 2e4)
                    if '1' in name:
                        actor.location.x = 700
                    elif '2' in name:
                        actor.location.x = 850
                    elif '3' in name:
                        actor.location.x = 1000



    def play_magic_trick(self):
        pass

        """
        ue.log("magic tick: {}".format(self.ticker))
        magic_actor_index = 0
        for name, actor in self.actors.items():
            if name in self.params['magic']['actor']:
                break
            magic_actor_index += 1
        location = self.check_array['location'][0][self.params['magic']['tick'][(self.params['magic']['tick'].index(self.ticker) + 2) % len(self.params['magic']['tick'])]][magic_actor_index][0]
        print("from frame {} to frame {}".format(self.ticker, self.params['magic']['tick'][(self.params['magic']['tick'].index(self.ticker) + 2) % len(self.params['magic']['tick'])]))
        magic_actor.set_location(location)
        """

    def tick(self):
        super().tick()
        if self.run > 1 and len(self.ordered_equations) != 0:
            magic_actor = self.actors[self.params['magic']['actor']]
            if math.isclose(magic_actor.actor.get_actor_location().y, (magic_actor.location.x - self.ordered_equations[0][0][1]) / self.ordered_equations[0][0][0], abs_tol=20):
                magic_actor.set_location(FVector(magic_actor.location.x, (magic_actor.location.x - self.ordered_equations[0][1][1]) / self.ordered_equations[0][1][0], magic_actor.location.z))
                del(self.ordered_equations[0])
            """
            for i in range(len(self.linear_equations)):
                if math.fabs(magic_actor.actor.get_actor_location().y - (magic_actor.location.x - self.linear_equations[i][1]) / self.linear_equations[i][0]) < 20:
                    print(math.fabs(magic_actor.actor.get_actor_location().y - (magic_actor.location.x - self.linear_equations[i][1]) / self.linear_equations[i][0]))
                if math.isclose(magic_actor.actor.get_actor_location().y, (magic_actor.location.x - self.linear_equations[i][1]) / self.linear_equations[i][0], abs_tol=20):
                    # print("{}: change from {} to {}".format(self.ticker, i, (i + 2) % len(self.linear_equations)))
                    magic_actor.set_location(FVector(magic_actor.location.x, (magic_actor.location.x - self.linear_equations[(i + 2) % len(self.linear_equations)][1]) / self.linear_equations[(i + 2) % len(self.linear_equations)][0], magic_actor.location.z))
                    break;
            """


    # We avoid comparing the locations of the magic actor during magic tick
    def set_magic_tick(self):
        if (Test.set_magic_tick(self) is False):
            return False

    def setup_magic_actor(self):
        self.ordered_equations = []
        magic_actor = self.actors[self.params['magic']['actor']]
        if self.run == 3:
            self.params[self.params['magic']['actor']].location.y *= -1
            magic_actor.location.y *= -1
            print('changing')
        if magic_actor.location.y < 0:
            self.ordered_equations.append([self.linear_equations[0], self.linear_equations[2]])
            self.ordered_equations.append([self.linear_equations[3], self.linear_equations[1]])
            self.ordered_equations.append([self.linear_equations[2], self.linear_equations[0]])
            self.ordered_equations.append([self.linear_equations[1], self.linear_equations[3]])
            print('left')
        elif magic_actor.location.y > 0:
            self.ordered_equations.append([self.linear_equations[3], self.linear_equations[1]])
            self.ordered_equations.append([self.linear_equations[0], self.linear_equations[2]])
            self.ordered_equations.append([self.linear_equations[1], self.linear_equations[3]])
            self.ordered_equations.append([self.linear_equations[2], self.linear_equations[0]])
            print('right')

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
        self.check_array['visibility'][0] = \
            remove_invisible_frames(self.check_array['visibility'][0])
        self.check_array['visibility'][1] = \
            remove_invisible_frames(self.check_array['visibility'][1])
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        # We need to separate occlusions because in the O3 bloc,
        # The objects are not at the same place at each run
        occlusion = separate_period_of_occlusions(visibility_array)
        self.params['magic']['tick'] = random.choice(occlusion[1])
        return True

    def dynamic_2_occluded(self):
        self.check_array['visibility'][0] = \
            remove_invisible_frames(self.check_array['visibility'][0])
        self.check_array['visibility'][1] = \
            remove_invisible_frames(self.check_array['visibility'][1])
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        occlusion = separate_period_of_occlusions(visibility_array)
        if (len(occlusion) < 4):
            return False;
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        self.params['magic']['tick'].append(random.choice(occlusion[2]))
        self.params['magic']['tick'].append(random.choice(occlusion[3]))
        return True
