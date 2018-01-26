import random

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import CameraComponent
from unreal_engine.enums import ECameraProjectionMode
from baseActor import BaseActor

class Camera(BaseActor):
    def __init__(self, rotation = None, location = None):
        self.field_of_view = 90
        self.aspect_ratio = 1
        self.projection_mode = ECameraProjectionMode.Perspective
        if (rotation == None or location == None):
            location, rotation = self.get_test_parameters()
        BaseActor.__init__(self, location, rotation)

    @staticmethod
    def get_train_parameters():
        """Returns random coordinates for train scenes
        In train scenes, camera has a high variability. Only the roll
        is forced to 0.
        """
        location = FVector(
            random.uniform(-100, 100),
            random.uniform(200, 400),
            100 + random.uniform(-30, 80))
        rotation = FRotator(
            0,
            random.uniform(-15, 10),
            random.uniform(-30, 30))
        return location, rotation

    @staticmethod
    def get_test_parameters():
        """Returns random coordinates for test scenes
        In test scenes, the camera has a constrained location, with
        little variations along the y axis and pitch.
        """
        location = FVector(
            0,
            -100 * random.random(),
            150)
        rotation = FRotator(
            0,
            -10 * random.random(),
            0)
        return location, rotation
