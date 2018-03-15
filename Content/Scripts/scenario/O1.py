from scenario import base


class O1Base(object):
    name = 'O1'


class O1Train(base.BaseTrain, O1Base):
    pass


class O1Test(base.BaseTest, O1Base):
    def get_nruns_check(self):
        nruns = 0
        if not self.is_occluded:
            nruns = 0
        elif self.ntricks == 2:
            nruns = 2
        else:  # occluded single trick
            nruns = 1
