import abc
import random

from unreal_engine import FVector, FRotator

from actors.parameters import *
from tools.materials import get_random_material_for_category


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

    def magic_setup(self, run_index):
        pass

    def generate_parameters(self):
        """Return a dict of {actor: parameters} for that scenario

        This method should be specialized in child classes. At the
        base level only the actors common to all scenarii are
        considered.

        """
        params = {}

        params['floor'] = FloorParams(
            material=get_random_material_for_category('Floor'))

        params['light'] = LightParams(
            type='SkyLight',
            location=FVector(0, 0, 1000),
            rotation=FRotator(0, 0, 0))

        prob_wall = 0
        if random.uniform(0, 1) <= prob_wall:
           params['walls'] = WallsParams(
               material=get_random_material_for_category('Wall'),
               height=random.uniform(1, 10),
               length=random.uniform(1500, 4000),
               depth=random.uniform(900, 1500))

        return params


class BaseTrain(Base):
    def get_description(self):
        return self.name + ' train'

    def get_nruns(self):
        return 1

    def is_train(self):
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

    @abc.abstractmethod
    def get_nchecks(self):
        """Return the total number of check runs needed by this scenario"""
        pass
