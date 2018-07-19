import random
from scenario.fullTest import FullTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
from unreal_engine import FVector
from scenario.checkUtils import checks_time_laps
from scenario.checkUtils import remove_last_and_first_frames
from scenario.checkUtils import remove_invisible_frames
from scenario.checkUtils import separate_period_of_occlusions
from scenario.checkUtils import store_actors_locations
from scenario.checkUtils import remove_frames_close_to_magic_tick
import unreal_engine as ue


class O4Base:
    @property
    def name(self):
        return 'O4'

    @property
    def description(self):
        return 'energy conservation'


class O4Train(O4Base, Train):
    pass


class O4Test(O4Base, FullTest):
    def __init__(self, world, saver, is_occluded, movement):
        if 'static' in movement:
            ue.log_warning("Static case is not implemented for this bloc")
            raise NotImplementedError
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]

    def generate_parameters(self):
        super().generate_parameters()

    def setup_magic_actor(self):
        magic_actor = self.actors[self.params['magic']['actor']]
        new_location = magic_actor.location
        if 'dynamic' in self.movement:
            new_location.y *= -1
        else:
            new_location.y *= -1
            # if static must change place between left actor and right actor
            for name, actor in self.actors.items():
                temp = actor.actor.get_actor_location()
                if temp == new_location and \
                        name != self.params['magic']['actor']:
                    temp.y *= -1
                    magic_actor.actor.set_actor_location(new_location + 1000)
                    actor.actor.set_actor_location(temp)
                    actor.location = temp
                elif 'occluder' in name:
                    temp = FVector(400, (new_location.y / 2) -
                                   (actor.scale.x * 200), 0)
                    actor.actor.set_actor_location(temp)
        ue.log(magic_actor.actor.get_actor_location())
        ue.log(new_location)
        magic_actor.actor.set_actor_location(new_location)
        ue.log(magic_actor.actor.get_actor_location())
        magic_actor.location = new_location
        magic_actor.initial_force.y *= -1
        # magic_actor = self.actors[self.params['magic']['actor']]
        pass

    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        location = store_actors_locations(self.actors)
        self.check_array['location'][self.run].append(location)
        frame = (self.ticker / 2) - 0.5
        IsActorInFrame = ScreenshotManager.IsActorInFrame(magic_actor, frame)
        self.check_array['visibility'][self.run].append(IsActorInFrame)

    def play_magic_trick(self):
        magic_actor = self.actors[self.params['magic']['actor']]
        magic_actor.reset_force()
        if random.choice([0, 1]) == 1:
            magic_actor.set_force(magic_actor.initial_force, False)

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
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        visibility_array = remove_invisible_frames(visibility_array)
        self.params['magic']['tick'] = random.choice(visibility_array)
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
