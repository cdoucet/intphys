from collections import defaultdict

import unreal_engine as ue
from unreal_engine import FVector, FRotator

from actors.base_actor import BaseActor
from actors.parameters import LightParams


class Light(BaseActor):
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
    If you don't send either the location and the rotation during the camera instantiation,
    the __init__ function will change it on its own
    """
    def __init__(self, world=None, params=LightParams()):
        types = {
            'Directional': '/Game/DirectionalLight.DirectionalLight_C',
            'SkyLight': '/Game/SkyLight.SkyLight_C',
            'PointLight': '/Game/PointLight.PointLight_C'
            }

        if world is not None:
            super().__init__(world.actor_spawn(ue.load_class(types[params.type])))

            # the position does not affect sky light
            if params.type != 'SkyLight':
                self.get_parameters(params)
                self.set_parameters()

            self.type = params.type
        else:
            super().__init__()

    def get_parameters(self, params):
        super().get_parameters(params.location, params.rotation, True, False)

    def set_parameters(self):
        super().set_parameters()

        # deactivate the physics (we don't want the light to fall)
        self.get_mesh().set_simulate_physics(False)

    def begin_play(self):
        self.set_actor(self.uobject.get_owner())

    def get_status(self):
        if self.type != 'SkyLight':
            status = super().get_status()
        else:
            status = defaultdict(list)
            status['actor'] = self.actor.get_name()
        status['type'] = self.type
        return status
