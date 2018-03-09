import unreal_engine as ue
from unreal_engine import FVector, FRotator
from actors.base_actor import BaseActor
from collections import defaultdict


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
                 world=None,
                 type="SkyLight",
                 location=FVector(0, 0, 0),
                 rotation=FRotator(0, 0, 0),
                 overlap=True,
                 warning=False):
        types = {
            'Directional': '/Game/DirectionalLight.DirectionalLight_C',
            'SkyLight': '/Game/SkyLight.SkyLight_C',
            'PointLight': '/Game/PointLight.PointLight_C'
            }
        if (world is not None):
            super().__init__(world.actor_spawn(ue.load_class(types[type])))
            if (type != 'SkyLight'):
                self.get_parameters(location, rotation, overlap, warning)
                self.set_parameters()
            self.type = type
        else:
            super().__init__()

    def get_parameters(self, location, rotation, overlap, warning):
        super().get_parameters(location, rotation, overlap, warning)

    def set_parameters(self):
        super().set_parameters()

    def begin_play(self):
        self.set_actor(self.uobject.get_owner())

    def get_status(self):
        if (self.type != 'SkyLight'):
            status = super().get_status()
        else:
            status = defaultdict(list)
            status['actor'] = self.actor.get_name()
        status['type'] = self.type
        return status
