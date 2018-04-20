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

    def apply_magic_trick(self):
        print("magic trick")
        self.runs[self.run].actors[self.params['magic']['actor']].set_hidden(True)
