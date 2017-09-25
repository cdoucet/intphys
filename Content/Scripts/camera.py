"""This module manages the scene's camera.

It defines and controls it's location and rotation.

The other camera parameters are constant and fixed in UE:
- a perspective projection,
- a ratio heigth/width fixed at 1 (to nsure a square image),
- an horizontal field of view of 90 degrees.
TODO implement this in Python

"""

import random

from unreal_engine import FVector, FRotator
import unreal_engine as ue


class CameraPythonComponant:
    def __init__(self):
        ue.log('camera init...')

    def get_train_parameters(self):
        """Returns random coordinates for train scenes

        In train scenes, camera has a high variability. Only the roll
        is forced to 0.

        """
        location = FVector(
            150 + random.uniform(-100, 100),
            30 + random.uniform(200, 400),
            80 + random.uniform(-10, 100))

        rotation = FRotator(
            random.uniform(-15, 10),
            -90 + random.uniform(-30, 30),
            0)

        return location, rotation

    def get_test_parameters(self):
        """Returns random coordinates for test scenes

        In test scenes, the camera has a constrained location, with
        little variations along the y axis and pitch.

        """
        location = FVector(150, -100 * random.random(), 150)
        rotation = FRotator(-10 * random.random(), -90, 0)

        return location, rotation

    def begin_play(self):
        ue.log('Camera begin play...')

    def on_actor_begin_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps the camera"""
        message = 'Camera overlaping {}'.format(other.get_name())

        ue.log(message)
        ue.log_error(message)
        raise RuntimeError(message)

    def get_status(self):
        """Returns the camera coordinates as a string"""
        location = self.uobject.get_actor_location()
        rotation = self.uobject.get_actor_rotation()

        return ' '.join(
            location.x, location.y, location.z,
            rotation.pitch, rotation.yaw, rotation.roll)
