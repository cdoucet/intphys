import abc
import random

from unreal_engine import FVector, FRotator

from actors.parameters import FloorParams, LightParams, WallsParams, SkySphereParams
from tools.materials import get_random_material


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

    @abc.abstractmethod
    def is_train(self):
        """Return True if this is a train scenario, False otherwise"""
        pass

    def is_test(self):
        """Return True if this is a test scenario, False otherwise"""
        return not self.is_train()

    @abc.abstractmethod
    def is_possible(self, run_index):
        """Return True if the current scene is physically plausible

        Train scenes are always possible. Test scenes have runs (1, 2)
        impossible and runs (3, 4) possible, ignoring the check runs
        if any.

        """
        pass

    def get_status(self, run_index):
        """Return a dict describing the scenario"""
        status = {
            'name': self.name,
            'type': 'test' if self.is_test() else 'train',
            'is_possible': self.is_possible(run_index)}

        return status

    def generate_parameters(self):
        """Return a the common paramaters for all the scenarios

        This method should be specialized in child classes. At the
        base level only the floor, background walls and lights are
        considered.

        """
        params = {}
        params['floor'] = FloorParams(
            material=get_random_material('Floor'))
        params['light'] = LightParams(
            type='SkyLight',
            location=FVector(0, 0, 1000),
            rotation=FRotator(0, 0, 0))

        params['skysphere'] = SkySphereParams()

        # the probability to have background walls
        prob_walls = 1
        if random.uniform(0, 1) <= prob_walls:
            params['walls'] = WallsParams(
                material=get_random_material('Wall'),
                height=random.uniform(1, 10),
                length=random.uniform(2000, 5000),
                depth=random.uniform(1500, 5000))
        return params


class BaseTrain(Base):
    def get_description(self):
        return self.name + ' train'

    def get_nruns(self):
        return 1

    def is_train(self):
        return True

    def is_possible(self, run_index):
        # A train scene is always possible
        return True


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
        return 4 + self.get_nchecks()

    def is_train(self):
        return False

    def is_possible(self, run_index):
        # A test scene is possible on runs 3 and 4 (minus the
        # checks). With this definition, a check scene is always
        # impossible.
        return True if run_index - self.get_nchecks() in (3, 4) else False

    @abc.abstractmethod
    def get_nchecks(self):
        """Return the total number of check runs needed by this scenario"""
        pass

    @abc.abstractmethod
    def setup_magic_trick(self, actor, run):
        pass

    @abc.abstractmethod
    def apply_magic_trick(self, actor, run):
        pass
