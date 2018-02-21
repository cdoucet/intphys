import unreal_engine as ue
from unreal_engine import FVector

from actors.floor import Floor


class BaseScene:
    def __init__(self, world, scenario):
        self.world = world
        self.scenario = scenario
        self.current_run = 0

    def get_nruns(self):
        return 1

    def get_nruns_remaining(self):
        return self.get_nruns() - self.current_run

    def is_valid(self):
        return True

    def is_train_scene(self):
        raise NotImplementedError

    def is_check_run(self):
        return False

    def description(self):
        """Return a string description of the scene's current run"""
        raise NotImplementedError

    def render(self):
        # TODO generate parameters and spawn the actors
        floor = Floor(self.world, scale=FVector(100, 100, 1))

        # prepare for the next run
        self.current_run += 1


class TrainScene(BaseScene):
    def __init__(self, world, scenario):
        super(TrainScene, self).__init__(world, scenario)

    def description(self):
        return self.scenario + ' train'

    def is_train_scene(self):
        return True


class TestScene(BaseScene):
    def __init__(
            self, world, scenario,
            is_occluded=False, is_static=False, ntricks=1):
        super(TestScene, self).__init__(world, scenario)

        self.is_occluded = is_occluded
        self.is_static = is_static
        self.ntricks = ntricks

    def description(self):
        return self.scenario + ' test ({}/{})'.format(
            self.current_run+1, self.get_nruns())

    def is_train_scene(self):
        return False

    def is_check_run(self):
        return self.current_run < self.get_nruns_check()

    def get_nruns(self):
        return 4 + self.get_nruns_check()

    def get_nruns_check(self):
        # TODO should be retrieved for scenario class
        nruns = 0
        if not self.is_occluded:
            nruns = 0
        elif self.ntricks == 2:
            nruns = 2
        else: # occluded single trick
            nruns = 1

        # block O2 has twice the checks of block O1
        if 'O2' in self.scenario:
            nruns *= 2

        return nruns
