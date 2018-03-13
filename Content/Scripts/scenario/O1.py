from scenario import base


class BaseO1(object):
    name = 'O1'


class O1Train(base.BaseTrain, O1):
    pass


class O1Test(base.BaseTest, O1):
    def get_nruns_check(self):
        nruns = 0
        if not self.is_occluded:
            nruns = 0
        elif self.ntricks == 2:
            nruns = 2
        else:  # occluded single trick
            nruns = 1
