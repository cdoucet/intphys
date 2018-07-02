"""Block O3 is spatio-temporal continuity, spheres only"""
import random
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from scenario.test import Test
from unreal_engine import FVector
from unreal_engine.classes import ScreenshotManager
import unreal_engine as ue


class O3Base:
    @property
    def name(self):
        return 'O3'

    @property
    def description(self):
        return 'bloc O3'


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
                pass
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
        try:
            for frame in range(5):
                visibility_array.remove(visibility_array[0])
                visibility_array.remove(visibility_array[-1])
        except IndexError:
            pass
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], True)
        try:
            for frame in range(5):
                visibility_array.remove(visibility_array[0])
                visibility_array.remove(visibility_array[-1])
        except IndexError:
            pass
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], True)
        try:
            for frame in range(5):
                visibility_array.remove(visibility_array[0])
                visibility_array.remove(visibility_array[-1])
        except IndexError:
            pass
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
        # because we want the second one or the object will be out the screen
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
        self.params['magic']['tick'] = random.choice(occlusion[1])
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
