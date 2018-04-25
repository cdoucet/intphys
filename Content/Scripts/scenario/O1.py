"""Block O1 is apparition/disparition, spheres only"""
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
