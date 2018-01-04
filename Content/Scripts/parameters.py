"""Handles random paramters generation for a given scene"""

import random


class TrainParameters(object):
    # the list of known (implemented) blocks
    _blocks = ['block_O1']

    def __init__(self, block):
        assert block in self._blocks
        self.block = block


class TestParameters(object):
    # visibility states in the scene (either we have occlusions or
    # not)
    visibilities = ['visible', 'occluded']

    #

    def __init__(self):
        pass

    def generate_train(self, block):


    def generate_test(self, block, type, visibility):
        assert visibility in self.visibilities
