import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseMesh import BaseMesh
import tools.materials

class Wall(BaseMesh):
    def __init__(self, world = None):
        ue.log('init enclosing wall')
    #    if (world != None):
    #        BaseMesh.__init__(self, world.actor_spawn(ue.load_class('/Game/Wall.Wall_C')), '/Game/Meshes/Floor_400x400', FVector(-200, -720, 0), FRotator(0, 0, 0), tools.materials.load_materials('Materials/Floor'), FVector(10, 10, 1), 1.0, FVector(-1e2, 0.0, 0.0))
    #    else:
    #        BaseMesh.__init__(self)
