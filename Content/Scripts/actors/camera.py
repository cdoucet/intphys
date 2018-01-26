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

    def begin_play(self):
        # retrieve the camera object from its Python component
        self.actor = self.uobject.get_owner()

        # OnActorBeginOverlap events are redirected to the
        # manage_overlap method
        self.actor.bind_event(
            'OnActorBeginOverlap', self.manage_overlap)

        # setup camera attributes
        camera_component = self.actor.get_component_by_type(CameraComponent)
        camera_component.SetFieldOfView(self.field_of_view)
        camera_component.SetAspectRatio(self.aspect_ratio)
        camera_component.SetProjectionMode(self.projection_mode)

        # place the camera at the desired coordinates
        self.actor.set_actor_location(self.location)
        self.actor.set_actor_rotation(self.rotation)

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps the camera"""
        # TODO the scene must fail here, this is a critical error
        message = 'Camera overlapping {}'.format(other.get_name())
        ue.log_error(message)

    def get_status(self):
        """Returns the camera coordinates as a string"""
        location = self.uobject.get_actor_location()
        rotation = self.uobject.get_actor_rotation()

        return ' '.join(
            location.x, location.y, location.z,
            rotation.pitch, rotation.yaw, rotation.roll)
