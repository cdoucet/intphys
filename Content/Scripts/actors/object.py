import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseMesh import BaseMesh
import tools.materials

class Object(BaseMesh):
    shape = {
        'Sphere': '/Engine/EngineMeshes/Sphere.Sphere',
        'Cube': '/Engine/EngineMeshes/Cube.Cube',
        # Cone seems to be gone somehow
        # 'Cone': '/Engine/EngineMeshes/Cone.Cone',
        # And Cylinder seems soooo far away
        'Cylinder': '/Engine/EngineMeshes/Cylinder.Cylinder'
    }

    def __init__(self, mesh_str = shape['Sphere'], world = None, location = FVector(0, 0, 0), rotation = FRotator(0, 0, 0), material = None, scale = FVector(1, 1, 1), mass = 1.0, force = FVector(-1e2, 0.0, 0.0)):
        if (world != None):
            BaseMesh.__init__(self, world.actor_spawn(ue.load_class('/Game/Object.Object_C')),
                              mesh_str, location, rotation, tools.materials.load_materials('Materials/Actor'), scale, mass, force)
            # Enable physic on that object
            self.get_mesh().set_simulate_physics()
            self.get_mesh().add_force(self.force)

        else:
            BaseMesh.__init__(self)

