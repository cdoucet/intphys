"""Block O3 is spatio-temporal continuity, spheres only"""
import math
import random
import unreal_engine as ue
from scenario.test import Test
from scenario.train import Train
from unreal_engine import FVector
from unreal_engine.classes import ScreenshotManager


class O3Base:
    @property
    def name(self):
        return 'O3'

    @property
    def description(self):
        return 'bloc O3'


class O3Train(O3Base, Train):
    pass


class O3Test(O3Base, Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(self, world, saver, is_occluded, movement)
        self.check_array[0]['visibility'] = []
        self.check_array[0]['location'] = []

    """
    def generate_parameters(self):
        super().generate_parameters()
        if self.is_occluded is True:
            if '1' in self.movement:
                self.params['occluder_1'].scale = FVector(1.5, 1, 1.5)
            elif '2' in self.movement:
                self.params['occluder_1'].scale = FVector(1, 1, 1.5)
                self.params['occluder_2'].scale = FVector(1, 1, 1.5)
    """

    def setup_magic_actor(self):
        # magic actor spawn hidden if it is the second possible run
        if self.run == 1:
            magic_actor = self.actors[self.params['magic']['actor']]
            current_location = magic_actor.actor.get_actor_location()
            target_location = FVector(0, 0, 0)
            if 'static' in self.movement:
                target_location = FVector(current_location.x + random.randint(10, 100),
                                          current_location.y,
                                          current_location.z)
            elif '1' in self.movement:
                target_location = FVector(current_location.x,
                                          current_location.y + 50,
                                          current_location.z)
            else:
                target_location = FVector(current_location.x,
                                          current_location.y + 200,
                                          current_location.z)
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

    def static_visible(self, check_array):
        count = 0
        while count < 50:
            count += 1
            self.params['magic']['tick'] = random.randint(10, 190)
            # check if actor is not visible during magic tick
            if check_array[self.params['magic']['tick']][0] is not True:
                continue
            return True
        ue.log_warning("to many try to find a magic tick")
        return False

    def dynamic_1_visible(self, check_array):
        count = 0
        while count < 50:
            count += 1
            self.params['magic']['tick'] = random.randint(10, 190)
            # check if actor is not visible during magic tick
            if check_array[self.params['magic']['tick']][0] is not True:
                continue
            return True
        ue.log_warning("to many try to find a magic tick")
        return False

    def dynamic_2_visible(self, check_array):
        count = 0
        visibility_changes = self.process(0, check_array)
        # if the actor is visible at the begining,
        # the first possible magic tick is 0, else it is the first frame when
        # the magic actor is visible
        if len(visibility_changes) > 0:
            start = 0 if check_array[0][0] is True else visibility_changes[0]
            if check_array[0][0] is True:
                end = visibility_changes[0] - 1
            elif len(visibility_changes) > 1:
                end = visibility_changes[1] - 1
            else:
                end = 199
        else:
            start = 0
            end = 199
        self.params['magic']['tick'] = [0, 0]
        while count < 50:
            count += 1
            self.params['magic']['tick'][0] = random.randint(start, end - 20)
            # minimum 10 ticks between each magic tick
            self.params['magic']['tick'][1] = random.randint(self.params['magic']['tick'][0] + 10, end)
            # check if actor is not visible during magic ticks
            if check_array[self.params['magic']['tick'][0]][0] is not True or \
                    check_array[self.params['magic']['tick'][1]][0] is not True or \
                    self.params['magic']['tick'][0] == \
                    self.params['magic']['tick'][1]:
                continue
            return True
        ue.log_warning("to many try to find a magic tick")
        return False

    def static_occluded(self, check_array):
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 2:
            ue.log_warning("not enough visibility changes")
            return False
        magic_tick = math.ceil((visibility_changes[1] + visibility_changes[0]) / 2)
        self.params['magic']['tick'] = magic_tick
        return True

    def dynamic_1_occluded(self, check_array):
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 2:
            ue.log_warning("not enough visibility changes")
            return False
        magic_tick = math.ceil((visibility_changes[1] + visibility_changes[0]) / 2)
        self.params['magic']['tick'] = magic_tick
        return True

    def dynamic_2_occluded(self, check_array):
        visibility_changes = self.process(0, check_array)
        if len(visibility_changes) < 4:
            ue.log_warning("not enough visibility changes")
            return False
        magic_tick = math.ceil((visibility_changes[1] + visibility_changes[0]) / 2)
        magic_tick2 = math.ceil((visibility_changes[2] + visibility_changes[3]) / 2)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(magic_tick)
        self.params['magic']['tick'].append(magic_tick2)
        return True
