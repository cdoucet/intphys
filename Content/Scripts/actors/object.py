# coding: utf-8

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material

from actors.base_mesh import BaseMesh
from actors.parameters import ObjectParams
from tools.materials import get_random_material_for_category


# Ok here we go:
# This is a recursive instantiate class.
# The general principle is to instantiate a class twice to avoid making two distinct classes.
# I needed to instantiate a python component with parameters but UnrealEnginePython
# wouldn't let me do that.
# Furthermore, I couldn't spawn the actor without instanciate the class and thus,
# I couldn't spawn it with any parameter.

# Let me explain myself :
# In the main, I call the constructor of the class Object (for instance, or Floor, or Occluder),
# which call the __init__ function of Object with at least 1 argument, world
# which call the __init__function of BaseMesh with at least 1 argument, mesh_str.
# In the Object __init__ function, I call actor_spawn,
# which implicitely instanciate Object (yes, again)
# BUT during the second instantiation, no parameters is given to __init__ (of Object and BaseMesh)
# (this is why there is default values to every parameters of __init__).
# Thus, if __init__ is called without any parameters, I know that it is the second instantiation,
# so I don't spawn the actor again.
# Once the object spawned, all I have to do is to set the parameters in the second instantiation
# (location, rotation,...).
# Et voilà !

# Object is the python component for the main actors of the magic tricks (the sphere, the cube, or else).
# It inherits from BaseMesh.



class Object(BaseMesh):
    """
    shape is a dictionnary with the path of every shape (mesh) available for the Object actor
    """
    shape = {
        'Sphere': '/Engine/EngineMeshes/Sphere.Sphere',
        'Cube': '/Engine/EngineMeshes/Cube.Cube',
        # Cone seems to be gone somehow
        # 'Cone': '/Engine/EngineMeshes/Cone.Cone',
        # And Cylinder seems way too small
        # 'Cylinder': '/Engine/EngineMeshes/Cylinder.Cylinder'
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
    def __init__(self,
                 world=None,
                 params=ObjectParams(),
                 overlap=False,
                 warning=True):
        if world is not None:
            super().__init__(world.actor_spawn(ue.load_class('/Game/Object.Object_C')))
            self.get_parameters(params)
            self.set_parameters()
        else:
            super().__init__()

    def get_parameters(self, params):
        super().get_parameters(
            params.location,
            params.rotation,
            params.scale,
            params.friction,
            params.restitution,
            False, True,
            self.shape[params.mesh])

        material = (get_random_material_for_category('Floor')
                    if params.material is None else params.material)
        self.material = ue.load_object(Material, material)
        self.mass = params.mass
        self.force = params.force

    def set_parameters(self):
        super().set_parameters()
        self.set_mass(self.mass)
        self.set_force(self.force)
        self.get_mesh().set_simulate_physics()

    """
    set the mass of the mesh
    to be honnest I don't really know what the second line do
    """
    def set_mass(self, mass):
        self.mass = mass
        self.mesh.SetMassScale(
            BoneName='None',
            InMassScale=self.mass / self.mesh.GetMassScale())

    def set_force(self, force):
        self.force = force

    """
    Apply force to the mesh
    """
    def move(self):
        self.get_mesh().add_force(self.force)

    def get_status(self):
        status = super().get_status()
        status['material'] = self.material.get_name()
        status['mass'] = self.mass
        status['force'].append(('x', self.force.x))
        status['force'].append(('y', self.force.y))
        status['force'].append(('z', self.force.z))
        return status
