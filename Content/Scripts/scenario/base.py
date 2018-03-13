import abc


class Base(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def name(self):
        """The name of the scenario (ie 'O1' or 'U2')"""
        pass

    @abc.abstractmethod
    def get_description(self):
        """A brief description of the scenario (ie 'O1 test visible static')"""
        pass

    @abc.abstractmethod
    def get_nruns(self):
        """The total number of runs needed for the scenario"""
        pass


class BaseTrain(Base):
    def get_description(self):
        return self.name + ' train'

    def get_nruns(self):
        return 1


class BaseTest(Base):
    def __init__(self, is_occluded=False, is_static=True, ntricks=1):
        self.is_occluded = is_occluded
        self.is_static = is_static
        self.ntricks = ntricks

    def get_description(self):
        return (
            self.name + ' test' +
            (' occluded' if self.is_occluded else ' visible') +
            (' static' if self.is_static else ' dynamic_{}'
             .format(self.ntricks)))

    def get_nruns(self):
        return 4 + self.get_nruns_check()

    @abc.abstractmethod
    def get_nruns_check(self):
        """Return the total number of check runs needed by this scenario"""
        pass
