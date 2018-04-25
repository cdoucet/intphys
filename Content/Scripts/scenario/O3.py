"""O3 is change of texture. Spheres only"""

from scenario.test import Test
from scenario.train import Train
from tools import materials


class O3Base:
    @property
    def name(self):
        return 'O3'

    @property
    def description(self):
        return 'bloc O3'


class O3Train(O3Base, Train):
    def __init__(self, world, saver):
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()


class O3Test(O3Base, Test):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)

    def generate_parameters(self):
        super().generate_parameters()

        # choose an alternative material different from the orginal one
        original = self.params[self.params['magic']['actor']].material
        new = original
        while new == original:
            new = materials.get_random_material('Object')
        self.params['magic']['material'] = new

    def setup_magic_actor(self):
        # on run 1 and 3 the magic actor is visible at start, on runs
        # 2 and 4 it is hidden (runs 1, 2 are impossible, runs 3, 4
        # are possible).
        run = self.run - self.get_nchecks() + 1
        if run in (2, 4):
            magic_actor = self.runs[self.run].actors[
                self.params['magic']['actor']]
            magic_actor.set_material(self.params['magic']['material'])

    def apply_magic_trick(self):
        # swap the material of the magic actor
        material_1 = self.params['magic']['material']
        material_2 = self.params[self.params['magic']['actor']].material

        magic_actor = self.runs[self.run].actors[self.params['magic']['actor']]
        if magic_actor.material.get_name() == material_2.split('.')[-1]:
            new_material = material_1
        else:
            new_material = material_2
        magic_actor.set_material(new_material)
