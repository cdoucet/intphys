import random

import unreal_engine as ue
from magical_value import MAGICAL_VALUE
from unreal_engine import FVector, FRotator
from actors.base_actor import BaseActor

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
    def __init__(self,
                 train = False,
                 world = None,
                 type = "Directional",
                 location = FVector(0, 0, MAGICAL_VALUE),
                 rotation = FRotator(0, 0, MAGICAL_VALUE),
                 manage_hits = True):
        types = {
            'Directional': '/Game/DirectionalLight.DirectionalLight_C',
            'SkyLight': '/Game/SkyLight.SkyLight_C',
            'PointLight': '/Game/PointLight.PointLight_C'
            }
        if (world != None):
            super().__init__(train, world.actor_spawn(ue.load_class(types[type])))
            if (type != 'SkyLight'):
                self.get_parameters(location, rotation, manage_hits)
                self.set_parameters()
        else:
            super().__init__()

    def get_parameters(self, location, rotation, manage_hits):
        super().get_parameters(location, rotation, manage_hits)

    def set_parameters(self):
        super().set_parameters()

    def begin_play(self):
        self.set_actor(self.uobject.get_owner())

    def get_status(self):
        status = super().get_status()
        return status
