import random
from scenario.fullTest import FullTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
from unreal_engine import FVector
import unreal_engine as ue


class O4Base:
    @property
    def name(self):
        return 'O4'

    @property
    def description(self):
        return 'bloc O4'


class O4Train(O4Base, Train):
    pass


class O4Test(O4Base, FullTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]

    def setup_magic_actor(self):
        magic_actor = self.actors[self.params['magic']['actor']]

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

    def play_magic_trick(self):
        ue.log("magic tick: {}".format(self.ticker))
        magic_actor = self.actors[self.params['magic']['actor']]
        magic_actor.reset_force()
        if random.choice([0, 1]) == 1:
            magic_actor.set_force(magic_actor.initial_force, False)

    def static_visible(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'][0], True)
        if len(visibility_array) < 17:
            ue.log_warning("Not enough visibility")
            return False
        for i in range(8):
            visibility_array.remove(visibility_array[-1])
            visibility_array.remove(visibility_array[0])
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'][0], True)
        if len(visibility_array) < 17:
            ue.log_warning("Not enough visibility")
            return False
        for frame in range(8):
            visibility_array.remove(visibility_array[0])
            visibility_array.remove(visibility_array[-1])
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'][0], True)
        if len(visibility_array) < 17:
            ue.log_warning("Not enough visibility")
            return False
        for frame in visibility_array:
            ue.log("1: {}".format(frame))
        for frame in range(5):
            visibility_array.remove(visibility_array[0])
            visibility_array.remove(visibility_array[-1])
        for frame in visibility_array:
            ue.log("2: {}".format(frame))
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        ue.log("magic tick {}".format(self.params['magic']['tick'][0]))
        for frame in range(6):
            if (visibility_array.index(self.params['magic']['tick'][0])
                    - frame in visibility_array):
                visibility_array.remove(visibility_array.
                                        index(self.params['magic']['tick'][0])
                                        - frame)
            if (visibility_array.index(self.params['magic']['tick'][0])
                    + frame in visibility_array):
                visibility_array.remove(visibility_array.
                                        index(self.params['magic']['tick'][0])
                                        + frame)
        for frame in visibility_array:
            ue.log("3: {}".format(frame))
        self.params['magic']['tick'].append(random.choice(visibility_array))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'][0], False)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'][0], False)
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
            ue.log_warning("Not enough occluded frame")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_occluded(self):
        # we only check the visibility of the first run because in the second
        # one the magic object is not visible
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'][0], False)
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
        if len(temp_array) < 2:
            ue.log_warning("not enough occluded frame")
            return False
        previous_frame = temp_array[0] - 1
        # distinguish the different occlusion time laps
        for frame in temp_array:
            if frame - 1 != previous_frame:
                i += 1
                occlusion.append([])
            occlusion[i].append(frame)
            previous_frame = frame
        # if there is less than 2 distinct occlusion the scene will restart
        if (len(occlusion) < 2 or
                len(occlusion[0]) == 0 or
                len(occlusion[1]) == 0):
            ue.log_warning("not enough occluded frame")
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        return True
