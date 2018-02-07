import random

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import CameraComponent
from unreal_engine.enums import ECameraProjectionMode
from unreal_engine.classes import KismetSystemLibrary, GameplayStatics
from baseActor import BaseActor



class Camera(BaseActor):
    """
    __init__ instantiate the class
    parameters ->
    world: UEngine world instance
    location: location of the actor (FVector). Default value: 0, 0, 0
    rotation: rotation of the actor (FRotator). Default value: 0, 0, 0
    field_of_view: angle of the camera field of view (int). Default value: 90
    aspect_ratio: I don't know what it is :(
    projection mode: I redirect you to the Unreal Engine Doc

    Warning !
    If you don't send either the location and the rotation
    or if you send them filled with 0, during the camera instantiation, 
    the __init__ function will change it on its own
    """
    def __init__(self,
                 world = None,
                 location = FVector(0, 0, 0),
                 rotation = FRotator(0, 0, 0),
                 field_of_view = 90,
                 aspect_ratio = 1,
                 projection_mode = ECameraProjectionMode.Perspective):
        self.field_of_view = field_of_view
        self.aspect_ratio = aspect_ratio
        self.projection_mode = projection_mode
        if (location == FVector(0, 0, 0) and rotation == FRotator(0, 0, 0)):
            location, rotation = self.get_test_parameters()
        if (world != None):
            BaseActor.__init__(self, world.actor_spawn(ue.load_class('/Game/Camera.Camera_C')),
                               location,
                               rotation)
            self.set_location(location)
            self.set_rotation(rotation)
            """Attach the viewport to the camera
            This initialization was present in the intphys-1.0 blueprint
            but seems to be useless in UE-4.17. This is maybe done by
            default.
            """
            player_controller = GameplayStatics.GetPlayerController(world, 0)
            player_controller.SetViewTargetWithBlend(NewViewTarget=self.actor)
        else:
            BaseActor.__init__(self)

    """
    Returns random coordinates for train scenes
    In train scenes, camera has a high variability. Only the roll
    is forced to 0.
    """
    @staticmethod
    def get_train_parameters():
        location = FVector(
            random.uniform(-100, 100),
            random.uniform(200, 400),
            100 + random.uniform(-30, 80))
        rotation = FRotator(
            0,
            random.uniform(-15, 10),
            random.uniform(-30, 30))
        return location, rotation

    """
    Returns random coordinates for test scenes
    In test scenes, the camera has a constrained location, with
    little variations along the y axis and pitch.
    """
    @staticmethod
    def get_test_parameters():
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
        self.set_actor(self.uobject.get_owner())
        self.actor.bind_event(
            'OnActorBeginOverlap', self.manage_overlap)
        camera_component = self.actor.get_component_by_type(CameraComponent)
        camera_component.SetFieldOfView(self.field_of_view)
        camera_component.SetAspectRatio(self.aspect_ratio)
        camera_component.SetProjectionMode(self.projection_mode)
