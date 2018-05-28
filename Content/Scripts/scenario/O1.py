"""Block O1 is apparition/disparition, spheres only"""
import random
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
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
        self.check_array[0]['visibility'] = []
        self.check_array[0]['location'] = []
        self.check_array[1]['visibility'] = []
        self.check_array[1]['location'] = []

    def setup_magic_actor(self):
        # magic actor spawn hidden if it is the second possible run
        is_hidden = True if self.run == 1 else False
        magic_actor = self.actors[self.params['magic']['actor']]
        magic_actor.set_hidden(is_hidden)

    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        self.check_array[self.run]['location'].append(
            magic_actor.get_actor_location())
        ignored_actors = []
        for actor_name, actor in self.actors.items():
            if 'object' not in actor_name.lower() and \
                    'occluder' not in actor_name.lower():
                if 'walls' in actor_name.lower():
                    ignored_actors.append(actor.front.actor)
                    ignored_actors.append(actor.left.actor)
                    ignored_actors.append(actor.right.actor)
                else:
                    ignored_actors.append(actor.actor)
        visible = ScreenshotManager.IsActorInLastFrame(
            magic_actor, ignored_actors)[0]
        self.check_array[self.run]['visibility'].append(visible)

    def tick(self):
        super().tick()
        magic_actor = self.actors[self.params['magic']['actor']].actor
        if ScreenshotManager.IsActorInFrame(magic_actor, self.ticker) is True:
            ue.log("{}: True".format(self.ticker))

    def static_visible(self):
        visibility_array = self.checks_time_laps("visibility", True)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = self.checks_time_laps('visibility', True)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = self.checks_time_laps('visibility', True)
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
        visibility_array = self.checks_time_laps('visibility', False)
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = self.checks_time_laps('visibility', False)
        # remove the last occurences of not visible actor if
        # it is out of the fieldview
        first = 0
        last = 199
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
        if len(visibility_array) < 1:
            ue.log_warning("Not enough visibility")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_occluded(self):
        visibility_array = self.checks_time_laps('visibility', False)
        temp_array = visibility_array
        # remove the first and last occurences of not visible actor if
        # it is out of the fieldview
        first = 0
        last = 199
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

    def set_magic_tick(self):
        if super().set_magic_tick() is False:
            return False
        if isinstance(self.params['magic']['tick'], int):
            magic_tick = self.params['magic']['tick']
            if self.check_array[0]['location'][magic_tick] == \
                    self.check_array[1]['location'][magic_tick]:
                ue.log_warning("Magic actor location doesn't match" +
                               "in each possible run")
                return False
        elif isinstance(self.params['magic']['tick'], list):
            magic_tick = self.params['magic']['tick']
            if self.check_array[0]['location'][magic_tick[0]] == \
                    self.check_array[1]['location'][magic_tick[0]] or \
                    self.check_array[0]['location'][magic_tick[1]] == \
                    self.check_array[1]['location'][magic_tick[1]]:
                ue.log_warning("Magic actor location doesn't match " +
                               "in each possible run")
                return False
