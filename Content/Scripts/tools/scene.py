import unreal_engine as ue

valid_scenarii = ['O1']


class BaseScene:
    def __init__(self, scenario):
        self.scenario = scenario

    def get_nruns(self):
        return 1


class TrainScene(BaseScene):
    def __init__(self, scenario):
        super(TrainScene, self).__init__(scenario)


class TestScene(BaseScene):
    def __init__(self, scenario, is_occluded=False, is_static=False, ntricks=1):
        super(TestScene, self).__init__(scenario)

        self.is_occluded = is_occluded
        self.is_static = is_static
        self.ntricks = ntricks

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
