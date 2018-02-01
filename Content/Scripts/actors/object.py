import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseMesh import BaseMesh
import tools.materials

"""
Ok here we go:
This is a recursive instantiate class.
The general principle is to instantiate a class twice to avoid making two distinct classes.
I needed to instantiate a python component with parameters but UnrealEnginePython
wouldn't let me do that.
Furthermore, I couldn't spawn the actor without instanciate the class and thus,
I couldn't spawn it with any parameter.

Let me explain myself :
In the main, I call the constructor of the class Object (for instance, or Floor, or Occluder),
which call the __init__ function of Object with at least 1 argument, world
which call the __init__function of BaseMesh with at least 1 argument, mesh_str.
In the Object __init__ function, I call actor_spawn,
which implicitely instanciate Object (yes, again)
BUT during the second instantiation, no parameters is given to __init__ (of Object and BaseMesh)
(this is why there is default values to every parameters of __init__).
Thus, if __init__ is called without any parameters, I know that it is the second instantiation,
so I don't spawn the actor again.
Once the object spawned, all I have to do is to set the parameters in the second instantiation
(location, rotation,...).
Et voilà !
"""

"""
Object is the python component for the main actors of the magic tricks (the sphere, the cube, or else).
It inherits from BaseMesh.
"""

class Object(BaseMesh):
    """
    shape is a dictionnary with the path of every shape (mesh) available for the Object actor
    """
    shape = {
        'Sphere': '/Engine/EngineMeshes/Sphere.Sphere',
        'Cube': '/Engine/EngineMeshes/Cube.Cube',
        # Cone seems to be gone somehow
        # 'Cone': '/Engine/EngineMeshes/Cone.Cone',
        # And Cylinder seems soooo far away
        'Cylinder': '/Engine/EngineMeshes/Cylinder.Cylinder'
    }

    """
    __init__ instantiate the class
    parameters ->
    world: UEngine world instance
    mesh_str: the path of the mesh/shape of the actor (str). Default value: a sphere
    location: location of the actor (FVector). Default value: 0, 0, 0
    rotation: rotation of the actor (FRotator). Default value: 0, 0, 0
    material: material of the actor (UObject). Default value: a random one in the relevant directory
    scale: scale of the actor (FVector). Default value: 1, 1, 1
    mass: mass of the actor (float). Default value: 1.0
    force: force applied to the actor (FVector) Default value: 0.0, 0.0, 0.0
    """
    def __init__(self, world = None,
                 mesh_str = shape['Sphere'],
                 location = FVector(0, 0, 0),
                 rotation = FRotator(0, 0, 0),
                 material = tools.materials.get_random_material(tools.materials.load_materials('Materials/Actor')),
                 scale = FVector(1, 1, 1),
                 mass = 1.0,
                 force = FVector(0.0, 0.0, 0.0)):
        if (world != None):
            BaseMesh.__init__(self,
                              world.actor_spawn(ue.load_class('/Game/Object.Object_C')),
                              mesh_str,
                              location,
                              rotation,
                              ue.load_object(Material, material),
                              scale,
                              mass,
                              force)
            # Enable physic on that object
            self.get_mesh().set_simulate_physics()
            self.get_mesh().add_force(self.force)

        else:
            BaseMesh.__init__(self)
