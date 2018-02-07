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
Floor is the plane thing which is the ground of the magic tricks.
It inherits from BaseMesh.
"""

class Floor(BaseMesh):
    """
    __init__ instantiate the class
    parameters ->
    world: UEngine world instance
    material: material of the actor (UObject). Default value: a random one in the relevant directory
    
    You can't pass the location, direction and so on of the floor as parameter
    because it is not needed, I gess
    If you need it anyway, help yourself
    Just for you to know, there is a formula in the location to make that the reference point 
    of the location is the center of the mesh, not the corner in the left back
    formula = 'the place where you want it to be' - (('size of the mesh' * 'scale') / 2
    so by default = 0 - (400 * 10) / 2
    the "- 10" for the yaw is because I want the reference point to be at the top side of the mesh,
    not in the middle of it.
    Disclaimer: if you change the size of the mesh, think about changing the formula
    """
    def __init__(self, world = None,
                 material = tools.materials.get_random_material(tools.materials.load_materials('Materials/Floor'))):
        scale = FVector(10, 10, 1)
        if (world != None):
            BaseMesh.__init__(self,
                              world.actor_spawn(ue.load_class('/Game/Floor.Floor_C')),
                              '/Game/Meshes/Floor_400x400',
                              FVector(0 - ((400 * scale.x) / 2), 0 - ((400 * scale.y) / 2), 0 - (10 * scale.z)),
                              FRotator(0, 0, 0),
                              ue.load_object(Material, material),
                              scale)
        else:
            BaseMesh.__init__(self)
