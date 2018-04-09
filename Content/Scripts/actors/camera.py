import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import CameraComponent
from unreal_engine.enums import ECameraProjectionMode
from unreal_engine.classes import GameplayStatics

from actors.base_actor import BaseActor
from actors.parameters import CameraParams


class Camera(BaseActor):
   def __init__(self, world=None, params=CameraParams()):
        if world is not None:
            super().__init__(world.actor_spawn(
                ue.load_class('/Game/Camera.Camera_C')))

            self.get_parameters(params)
            self.set_parameters(world)
        else:
            super().__init__()

    def get_parameters(self, params):
        self.field_of_view = params.field_of_view
        self.aspect_ratio = params.aspect_ratio
        self.projection_mode = params.projection_mode
        super().get_parameters(params.location, params.rotation, True, True)

    def set_parameters(self, world):
        super().set_parameters()

        # Attach the viewport to the camera. This initialization
        # was present in the intphys-1.0 blueprint but seems to be
        # useless in UE-4.17. This is maybe done by default.
        player_controller = GameplayStatics.GetPlayerController(world, 0)
        player_controller.SetViewTargetWithBlend(NewViewTarget=self.actor)

        self.camera_component = self.actor.get_component_by_type(
            CameraComponent)
        self.camera_component.SetFieldOfView(self.field_of_view)
        self.camera_component.SetAspectRatio(self.aspect_ratio)
        self.camera_component.SetProjectionMode(self.projection_mode)

    def set_field_of_view(self, field_of_view):
        self.field_of_view = field_of_view
        self.camera_component.SetFieldOfView(self.field_of_view)

    def set_aspect_ratio(self, aspect_ratio):
        self.aspect_ratio = aspect_ratio
        self.camera_component.SetAspectRatio(self.aspect_ratio)

    def set_projection_mode(self, projection_mode):
        self.projection_mode = projection_mode
        self.camera_component.SetProjectionMode(self.projection_mode)

    def begin_play(self):
        self.set_actor(self.uobject.get_owner())

    def get_status(self):
        status = super().get_status()
        status['field_of_view'] = self.field_of_view
        status['aspect_ratio'] = self.aspect_ratio
        status['projection_mode'] = self.projection_mode
        return status
