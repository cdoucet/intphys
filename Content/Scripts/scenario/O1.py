"""Block O1 is apparition/disparition, spheres only"""
import math
import random
import unreal_engine as ue
from scenario.test import Test
from scenario.train import Train


class O1Base:
    @property
    def name(self):
        return 'O1'

    @property
    def description(self):
        return 'bloc O1'


class O1Train(O1Base, Train):
    def __init__(self, world, saver):
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()


class O1Test(O1Base, Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)

    def generate_parameters(self):
        super().generate_parameters()

    def setup_magic_actor(self):
        # on run 1 and 3 the magic actor is visible at start, on runs
        # 2 and 4 it is hidden (runs 1, 2 are impossible, runs 3, 4
        # are possible).
        run = self.run - self.get_nchecks() + 1
        is_hidden = True if run in (2, 4) else False

        magic_actor = self.runs[self.run].actors[self.params['magic']['actor']]
        magic_actor.set_hidden(is_hidden)

    def apply_magic_trick(self):
        magic_actor = self.runs[self.run].actors[self.params['magic']['actor']]
        # revert the hidden state of the actor (hidden -> visible or
        # visible -> hidden)
        magic_actor.set_hidden(not magic_actor.hidden)

    def static_visible(self, check_array):
        count = 0
        while count < 50:
            count += 1
            self.params['magic']['tick'] = random.randint(50, 150)
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
            self.params['magic']['tick'] = random.randint(50, 150)
            # check if actor is not visible during magic tick
            if check_array[self.params['magic']['tick']][0] is not True:
                continue
            return True
        ue.log_warning("to many try to find a magic tick")
        return False

    def dynamic_2_visible(self, check_array):
        count = 0
        while count < 50:
            count += 1
            self.params['magic']['tick'][0] = random.randint(50, 150)
            self.params['magic']['tick'][1] = random.randint(50, 150)
            # check if actor is not visible during magic ticks
            if check_array[self.params['magic']['tick']][0] is not True or \
                    check_array[self.params['magic']['tick']][1] is not True or \
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

    def set_magic_tick(self, check_array):
        try:
            if self.is_occluded is True:
                if 'static' in self.movement:
                    self.static_occluded(check_array)
                elif 'dynamic_1' in self.movement:
                    self.dynamic_1_occluded(check_array)
                else:
                    self.dynamic_2_occluded(check_array)
            else:
                if 'static' in self.movement:
                    self.static_visible(check_array)
                elif 'dynamic_1' in self.movement:
                    self.dynamic_1_visible(check_array)
                else:
                    self.dynamic_2_visible(check_array)
        except Exception as e:
            ue.log_warning(e)
            return False
