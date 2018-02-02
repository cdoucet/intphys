import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseMesh import BaseMesh
import tools.materials

# For the moment the occluder is just a smaller floor put vertically
# TODO : search for the proper mesh, actor, materials and so on...

class Occluder(BaseMesh):
    def __init__(self, world = None, location = FVector(0, 0, 0), rotation(0, 0, 0), scale = FVector(1, 1, 1)):
        if (world != None):
            BaseMesh.__init__(self, world.actor_spawn(ue.load_class('/Game/Floor.Floor_C')), '/Game/Meshes/Floor_400x400', location, rotation, tools.materials.load_materials('Materials/Floor'), scale = scale)
        else:
            BaseMesh.__init__(self)
