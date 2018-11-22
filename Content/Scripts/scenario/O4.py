import random
import math
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
from unreal_engine import FVector

class O4Base:
    @property
    def name(self):
        return 'O4'

    @property
    def description(self):
        return 'energy conservation'


class O4Train(O4Base, Train):
    pass


class O4Test(O4Base, MirrorTest):
    def __init__(self, world, saver, is_occluded, movement):
        """
        if 'static' in movement:
            ue.log_warning("Static case is not implemented for this bloc")
            raise NotImplementedError
        """
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]

    def compare_location_in_frame(self, actor, frame):
        return True;

    def generate_parameters(self):
        super().generate_parameters()
        self.params['Camera'].location.x = -1000
        n = [0, 1, 2]
        for name, actor in self.params.items():
            if 'bject' in name:
                actor.mesh = 'Cube'
                actor.initial_force.z = 0
                r = random.choice(n)
                actor.location.x = 1000 + actor.scale.x * 100 * math.sqrt(3) * r
                n.remove(r)
            elif 'loor' in name:
                # TODO make it work
                actor.friction = -8000
                actor.restitution = 1000

    def setup_magic_actor(self):
        if self.run % 2 == 1:
            magic_actor = self.actors[self.params['magic']['actor']]
            new_location = magic_actor.location
            if 'static' in self.movement:
                # i must retrieve n from initial declaration in test::generate_parameters()
                n = (magic_actor.location.x - 1000) / (magic_actor.scale.x * 100 * math.sqrt(3))
                new_location.y = 1000 + n \
                    + magic_actor.scale.x * 100 * math.sqrt(3) * (n + 1)
                # TODO look if it works
                new_location.y = -1500
                # magic_actor.initial_force = FVector(0, (4e4 + (abs(new_location.y) - 1500) * 10) * (-1 if new_location.y > 0 else 1), 0)
                magic_actor.initial_force = FVector(0, 10000, 0)
                # magic_actor.mesh.set_physics_linear_velocity(FVector(0, 673.6220553700072, 0));
                # magic_actor.mesh.set_physics_linear_velocity(FVector(0, 673.6220553700072, 1091.116293091501));

                print("setup magic actor")
                if new_location.y > 0:
                    print(magic_actor.initial_force)
            else:
                new_location.y *= -1
                magic_actor.initial_force.y *= -1
            magic_actor.actor.set_actor_location(new_location)
            magic_actor.location = new_location

    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        location = store_actors_locations(self.actors)
        self.check_array['location'][self.run].append(location)
        frame = (self.ticker / 2) - 0.5
        IsActorInFrame = ScreenshotManager.IsActorInFrame(magic_actor, frame)
        self.check_array['visibility'][self.run].append(IsActorInFrame)

    """
    def play_magic_trick(self):
        ue.log("tick magic {}".format(self.ticker))
        magic_actor = self.actors[self.params['magic']['actor']]
        print("reset force play magic trick")
        magic_actor.reset_force()
        # if random.choice([0, 1]) == 1:
        # magic_actor.set_force(magic_actor.initial_force, False)
    """

    def static_visible(self):
        res = []
        tick = 0
        for tick in range(len(self.check_array['location'][0])):
            actor_index = 0
            for actor in self.actors:
                if (actor == self.params['magic']['actor']):
                    if ((tick != 0 and self.actors[actor].initial_force.y > 0 and
                         self.check_array['location'][1][tick - 1][actor_index][0].y <=
                         self.check_array['location'][0][tick][actor_index][0].y <=
                         self.check_array['location'][1][tick][actor_index][0].y) or
                        (tick != len(self.check_array['location'][0]) and self.actors[actor].initial_force.y < 0 and
                         self.check_array['location'][1][tick][actor_index][0].y <=
                         self.check_array['location'][0][tick][actor_index][0].y <=
                         self.check_array['location'][1][tick + 1][actor_index][0].y)):
                        res.append(tick)
                actor_index += 1
        if not res:
            return False
        self.params['magic']['tick'] = random.choice(res)
        return True

    def dynamic_1_visible(self):
        res = []
        tick = 0
        for tick in range(len(self.check_array['location'][0])):
            actor_index = 0
            for actor in self.actors:
                if (actor == self.params['magic']['actor'] and tick != 0 and
                        (self.check_array['location'][1][tick - 1][actor_index][0].y <=
                         self.check_array['location'][0][tick][actor_index][0].y <=
                         self.check_array['location'][1][tick][actor_index][0].y or
                         self.check_array['location'][0][tick - 1][actor_index][0].y <=
                         self.check_array['location'][1][tick][actor_index][0].y <=
                         self.check_array['location'][0][tick][actor_index][0].y)):
                    res.append(tick)
                actor_index += 1
        if not res:
            return False
        self.params['magic']['tick'] = random.choice(res)
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
        # TODO i could calculate the difference between the location of magic_actor in
        # two run to say if the difference is too big
        res = []
        tick = 0
        for tick in range(len(self.check_array['location'][0])):
            actor_index = 0
            for actor in self.actors:
                if (actor == self.params['magic']['actor'] and tick != 0 and
                        self.check_array['location'][1][tick - 1][actor_index][0].y <=
                        self.check_array['location'][0][tick][actor_index][0].y <=
                        self.check_array['location'][1][tick][actor_index][0].y):
                    res.append(tick)
                actor_index += 1
        if not res:
            return False
        self.params['magic']['tick'] = random.choice(res)
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
