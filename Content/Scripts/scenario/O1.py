"""Block O1 is apparition/disparition, spheres only"""
import random
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
from scenario.checkUtils import checks_time_laps
from scenario.checkUtils import remove_last_and_first_frames
from scenario.checkUtils import remove_invisible_frames
from scenario.checkUtils import separate_period_of_occlusions
from scenario.checkUtils import store_actors_locations
from scenario.checkUtils import remove_frames_close_to_magic_tick
import unreal_engine as ue


class O1Base:
    @property
    def name(self):
        return 'O1'

    @property
    def description(self):
        return 'object permanence'


class O1Train(O1Base, Train):
    pass


class O1Test(O1Base, MirrorTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]

    def setup_magic_actor(self):
        # magic actor spawn hidden if it is the second possible run
        is_hidden = True if self.run == 1 else False
        magic_actor = self.actors[self.params['magic']['actor']]
        magic_actor.set_hidden(is_hidden)

    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        location = store_actors_locations(self.actors)
        self.check_array['location'][self.run].append(location)
        frame = (self.ticker / 2) - 0.5
        IsActorInFrame = ScreenshotManager.IsActorInFrame(magic_actor, frame)
        self.check_array['visibility'][self.run].append(IsActorInFrame)

    def static_visible(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            checks_time_laps(self.check_array['visibility'][0], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            checks_time_laps(self.check_array['visibility'][0], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            checks_time_laps(self.check_array['visibility'][0], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 5)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        visibility_array = \
            remove_frames_close_to_magic_tick(visibility_array,
                                              self.params['magic']['tick'][0],
                                              5)
        self.params['magic']['tick'].append(random.choice(visibility_array))
        ue.log("magic tick 2 = {}".format(self.params['magic']['tick'][1]))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            checks_time_laps(self.check_array['visibility'][0], False)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            checks_time_laps(self.check_array['visibility'][0], False)
        visibility_array = remove_invisible_frames(visibility_array)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_occluded(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            checks_time_laps(self.check_array['visibility'][0], False)
        visibility_array = remove_invisible_frames(visibility_array)
        occlusion = separate_period_of_occlusions(visibility_array)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        return True
