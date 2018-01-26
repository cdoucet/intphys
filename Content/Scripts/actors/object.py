import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseMesh import BaseMesh

class Object(BaseMesh):
    def __init__(self, mesh_str = None, world = None, location = FVector(0, 0, 0), rotation = FRotator(0, 0, 0)):
        if (world != None):
            BaseMesh.__init__(self, world.actor_spawn(ue.load_class('/Game/Object.Object_C')),
                              mesh_str, location, rotation)
        else:
            BaseMesh.__init__(self)
