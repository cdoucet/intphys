from scenario import base


class O1Base(object):
    @property
    def name(self):
        return 'O1'


class O1Train(O1Base, base.BaseTrain):
    pass


class O1Test(O1Base, base.BaseTest):
    def get_nruns_check(self):
        nruns = 0
        if not self.is_occluded:
            nruns = 0
        elif self.ntricks == 2:
            nruns = 2
        else:  # occluded single trick
            nruns = 1
