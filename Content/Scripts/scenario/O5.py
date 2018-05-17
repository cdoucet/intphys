"""Block O5 is energy/momentum, spheres only"""
import random
from scenario.fullTest import FullTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
from unreal_engine import FVector
import unreal_engine as ue


class O5Base:
    @property
    def name(self):
        return 'O5'

    @property
    def description(self):
        return 'bloc O5'


class O5Train(O5Base, Train):
    pass


class O5Test(O5Base, FullTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)
        self.check_array[0]['visibility'] = []
        self.check_array[0]['location'] = []
        self.check_array[1]['visibility'] = []
        self.check_array[1]['location'] = []
        self.second = False

    """
    def generate_parameters(self):
        super().generate_paramaters()
        temp = self.params[self.params["magic"]["actor"]].location
        # the actors needs to be hidden from the screen
        for name, actor in self.params.items():
            if 'object' in name:
                actor.location.y = 1250 * -1 if temp < 0 else 1
    """

    def play_run(self):
        super().play_run()
        if 'static' not in self.movement:
            for name, actor in self.actors.items():
                if 'object' in name.lower():
                    actor.set_force(FVector(0, 0, 14e5))

    def setup_magic_actor(self):
        # two run out of four
        if self.run % 2 == 0:
            return
        magic_actor = self.actors[self.params['magic']['actor']]
        new_location = magic_actor.actor.get_actor_location()
        if 'dynamic' in self.movement:
            new_location.y *= -1
        else:
            new_location.y *= -1
            for name, actor in self.actors.items():
                temp = actor.actor.get_actor_location()
                if temp == new_location and \
                        name != self.params['magic']['actor']:
                    temp.y *= -1
                    magic_actor.actor.set_actor_location(new_location + 1000)
                    actor.actor.set_actor_location(temp)
                elif 'occluder' in name:
                    temp = FVector(400, (new_location.y / 2) -
                                   (actor.scale.x * 200), 0)
                    actor.actor.set_actor_location(temp)
        magic_actor.actor.set_actor_location(new_location)

    def play_magic_trick(self):
        ue.log("magic tick: {}".format(self.ticker))
        magic_actor = self.actors[self.params['magic']['actor']]
        # for dynamic 2, apply force on the first magic tick, remove it on the second one
        if self.second is False:
            magic_actor.set_force(FVector(0, 0, 980 *
                                          magic_actor.get_mesh().GetMass()), True)
        else:
            magic_actor.force.z = 0
        if 'static' in self.movement:
            magic_actor.set_force(FVector(0, 0, 24e5))
        self.second = True

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

    def static_visible(self):
        visibility_array = self.checks_time_laps("visibility", True)
        # if the number of frame where the magic actor is visible is less than
        # 4 time the number of magic tick required, scene need to be restarted
        if len(visibility_array) < 4:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = self.checks_time_laps('visibility', True)
        # if the number of frame where the magic actor is visible is less than
        # 4 time the number of magic tick required, scene need to be restarted
        if len(visibility_array) < 4:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = self.checks_time_laps('visibility', True)
        # if the number of frame where the magic actor is visible is less than
        # 4 time the number of magic tick required, scene need to be restarted
        if len(visibility_array) < 8:
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(visibility_array))
        visibility_array.remove(self.params['magic']['tick'][0])
        self.params['magic']['tick'].append(random.choice(visibility_array))
        self.params['magic']['tick'].sort()
        self.params['magic']['tick'].append(18)
        self.params['magic']['tick'].append(32)
        return True

    def static_occluded(self):
        visibility_array = self.checks_time_laps('visibility', False)
        # if the number of frame where the magic actor is visible is less than
        # 4 time the number of magic tick required, scene need to be restarted
        if len(visibility_array) < 4:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        self.params['magic']['tick'] = 100
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
        # if the number of frame where the magic actor is visible is less than
        # 4 time the number of magic tick required, scene need to be restarted
        if len(visibility_array) < 4:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        self.params['magic']['tick'] = 24
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
        if len(occlusion) < 2:
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(12)
        self.params['magic']['tick'].append(30)
        """
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        """
        return True

    def set_magick_tick(self):
        res = super().set_magic_tick()
        return res
