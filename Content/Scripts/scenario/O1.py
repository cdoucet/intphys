"""Block O1 is apparition/disparition, spheres only"""
import random
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
from unreal_engine import FVector
import unreal_engine as ue


class O1Base:
    @property
    def name(self):
        return 'O1'

    @property
    def description(self):
        return 'bloc O1'


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
        location = FVector()
        location.x = int(round(magic_actor.get_actor_location().x))
        location.y = int(round(magic_actor.get_actor_location().y))
        location.z = int(round(magic_actor.get_actor_location().z))
        self.check_array['location'][self.run].append(location)
        frame = (self.ticker / 2) - 0.5
        IsActorInFrame = ScreenshotManager.IsActorInFrame(magic_actor, frame)
        self.check_array['visibility'][self.run].append(IsActorInFrame)

    def static_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], True)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], True)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], True)
        if len(visibility_array) < 2:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        visibility_array.remove(self.params['magic']['tick'][0])
        self.params['magic']['tick'].append(random.choice(visibility_array))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], False)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], False)
        # remove the last occurences of not visible actor if
        # it is out of the fieldview
        first = 0
        last = 99
        try:
            while True:
                quit = False
                if visibility_array[0] == first:
                    visibility_array.remove(first)
                    first += 1
                else:
                    quit = True
                if visibility_array[-1] == last:
                    visibility_array.remove(last)
                    last -= 1
                elif quit is True:
                    break
        except IndexError:
            pass
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_occluded(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], False)
        temp_array = visibility_array
        # remove the first and last occurences of not visible actor if
        # it is out of the fieldview
        first = 0
        last = 99
        try:
            while True:
                quit = False
                if visibility_array[0] == first:
                    visibility_array.remove(first)
                    first += 1
                else:
                    quit = True
                if visibility_array[-1] == last:
                    visibility_array.remove(last)
                    last -= 1
                elif quit is True:
                    break
        except IndexError:
            pass
        temp_array = visibility_array
        occlusion = []
        occlusion.append([])
        i = 0
        previous_frame = temp_array[0] - 1
        # distinguish the different occlusion time laps
        for frame in temp_array:
            if frame - 1 != previous_frame:
                i += 1
                occlusion.append([])
            occlusion[i].append(frame)
            previous_frame = frame
        # if there is less than 2 distinct occlusion the scene will restart
        if len(occlusion) < 2:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        return True
