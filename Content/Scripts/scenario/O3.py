"""Block O3 is spatio-temporal continuity, spheres only"""
import random
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
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
        self.check_array[0]['visibility'] = []
        self.check_array[0]['location'] = []
        self.check_array[1]['visibility'] = []
        self.check_array[1]['location'] = []
        self.machin = 0

    def setup_magic_actor(self):
        if self.run == 1:
            magic_actor = self.actors[self.params['magic']['actor']]
            current_location = magic_actor.actor.get_actor_location()
            length = 0
            target_location = FVector(0, 0, 0)
            if 'static' in self.movement:
                length = random.randint(10, 500)
                target_location = FVector(current_location.x + length,
                                          current_location.y,
                                          current_location.z)
            elif '1' in self.movement:
                if magic_actor.actor.get_actor_location().y < 0:
                    length = random.randint(50, 150)
                    length = 300
                else:
                    length = random.randint(-150, 50)
                    length = -300
                target_location = FVector(current_location.x,
                                          current_location.y + length,
                                          current_location.z)
            else:
                if magic_actor.actor.get_actor_location().y < 0:
                    length = random.randint(50, 150)
                    length = 300
                else:
                    length = random.randint(-150, 50)
                    length = -300
                length = 100
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
        self.machin += 1
        if self.machin == 200:
            self.machin = 0

    def static_visible(self):
        visibility_array = self.checks_time_laps("visibility", True)
        if len(visibility_array) <= 0:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = self.checks_time_laps('visibility', True)
        if len(visibility_array) <= 0:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        self.params['magic']['tick'] = 120
        return True

    def dynamic_2_visible(self):
        visibility_array = self.checks_time_laps('visibility', True)
        if len(visibility_array) <= 1:
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        visibility_array.remove(self.params['magic']['tick'][0])
        self.params['magic']['tick'].append(random.choice(visibility_array))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        visibility_array = self.checks_time_laps('visibility', False)
        if len(visibility_array) <= 0:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = self.checks_time_laps('visibility', False)
        temp_array = visibility_array
        # remove the last occurences of not visible actor if
        # it is out of the fieldview
        if visibility_array[-1] == 199:
            previous_frame = 0
            for frame in reversed(temp_array):
                if frame == 199 or frame + 1 == previous_frame:
                    previous_frame = frame
                    visibility_array.remove(frame)
        if len(visibility_array) <= 0:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_occluded(self):
        visibility_array = self.checks_time_laps('visibility', False)
        temp_array = visibility_array
        # remove the last occurences of not visible actor if
        # it is out of the fieldview
        if visibility_array[-1] == 199:
            previous_frame = 0
            for frame in reversed(temp_array):
                if frame == 199 or frame + 1 == previous_frame:
                    previous_frame = frame
                    visibility_array.remove(frame)
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
        if len(occlusion) <= 1 or len(occlusion[0]) <= 0 \
                or len(occlusion[1]) <= 0:
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        return True
