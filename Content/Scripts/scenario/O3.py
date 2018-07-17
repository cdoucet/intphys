import random
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from scenario.test import Test
from unreal_engine import FVector
from unreal_engine.classes import ScreenshotManager
import unreal_engine as ue
from scenario.checkUtils import checks_time_laps
from scenario.checkUtils import remove_last_and_first_frames
from scenario.checkUtils import remove_invisible_frames
from scenario.checkUtils import separate_period_of_occlusions
from scenario.checkUtils import store_actors_locations


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
        for name, params in self.params.items():
            if 'ccluder' in name:
                if 'dynamic_1' in self.movement:
                    params.scale.x = 1.5
            elif name == self.params['magic']['actor']:
                # the magic object needs to fly because it won't be a
                # sphere at both run
                params.initial_force.z = 3e4 + \
                    (abs(params.location.y) - 1500) * 4
            elif 'bject' in name:
                pass

    # We avoid comparing the locations of the magic actor during magic tick
    def set_magic_tick(self):
        if (Test.set_magic_tick(self) is False):
            return False

    def setup_magic_actor(self):
        if self.run == 1:
            magic_actor = self.actors[self.params['magic']['actor']]
            current_location = magic_actor.actor.get_actor_location()
            length = 0
            target_location = FVector(0, 0, 0)
            if 'static' in self.movement:
                length = random.randint(300, 500)
                target_location = FVector(current_location.x + length,
                                          current_location.y,
                                          current_location.z)
            elif '1' in self.movement:
                if magic_actor.actor.get_actor_location().y > 0:
                    length = random.randint(300, 800)
                else:
                    length = random.randint(-800, -300)
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            else:
                if magic_actor.actor.get_actor_location().y > 0:
                    length = random.randint(200, 350)
                else:
                    length = random.randint(-350, -200)
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            ue.log("jump length = {}".format(length))
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
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        visibility_array.remove(self.params['magic']['tick'][0])
        self.params['magic']['tick'].append(random.choice(visibility_array))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        visibility_array = remove_invisible_frames(visibility_array)
        # We need to separate occlusions because in the O3 bloc,
        # The objects are not at the same place at each run
        occlusion = separate_period_of_occlusions(visibility_array)
        self.params['magic']['tick'] = random.choice(occlusion[1])
        return True

    def dynamic_2_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        visibility_array = remove_invisible_frames(visibility_array)
        occlusion = separate_period_of_occlusions(visibility_array)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        return True
