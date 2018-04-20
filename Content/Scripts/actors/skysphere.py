import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material

from actors.base_mesh import BaseMesh
from actors.parameters import FloorParams


class SkySphere(BaseMesh):
    def __init__(self, world=None, params=FloorParams()):
        if world is not None:
            super().__init__(world.actor_spawn(
                ue.load_class('/Game/Meshes/SkySphere/BP_Sky_Sphere.BP_Sky_Sphere_C')))
            self.mesh_str = '/Game/Meshes/SkySphere/SM_SkySphere'
            self.material = ue.load_object(Material, params.material)
            self.set_mesh()
        else:
            super().__init__()

    def get_parameters(self, params):
        location = FVector(0, 0, 0)

        super().get_parameters(
            location, FRotator(0, 0, 0), params.scale,
            params.friction, params.restitution, False, False,
            '/Game/Meshes/Floor_400x400')

        self.material = ue.load_object(Material, params.material)

    def set_parameters(self):
        super().set_parameters()
        self.get_mesh().call('SetCollisionProfileName BlockAll')

    def get_status(self):
        status = {
            'name': self.actor.get_name(),
            'material': self.material.get_name()}
        return status
