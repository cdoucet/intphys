# coding: utf-8

import unreal_engine as ue
from unreal_engine.classes import Material

from actors.base_mesh import BaseMesh
from actors.parameters import ObjectParams
from tools.utils import as_dict


# Ok here we go: This is a recursive instantiate class.  The general
# principle is to instantiate a class twice to avoid making two
# distinct classes.  I needed to instantiate a python component with
# parameters but UnrealEnginePython wouldn't let me do that.
# Furthermore, I couldn't spawn the actor without instanciate the
# class and thus, I couldn't spawn it with any parameter.

# Let me explain myself : In the main, I call the constructor of the
# class Object (for instance, or Floor, or Occluder), which call the
# __init__ function of Object with at least 1 argument, world which
# call the __init__function of BaseMesh with at least 1 argument,
# mesh_str.  In the Object __init__ function, I call actor_spawn,
# which implicitely instanciate Object (yes, again) BUT during the
# second instantiation, no parameters is given to __init__ (of Object
# and BaseMesh) (this is why there is default values to every
# parameters of __init__).  Thus, if __init__ is called without any
# parameters, I know that it is the second instantiation, so I don't
# spawn the actor again.  Once the object spawned, all I have to do is
# to set the parameters in the second instantiation (location,
# rotation,...).  Et voilà !

# Object is the python component for the main actors of the magic
# tricks (the sphere, the cube, or else).  It inherits from BaseMesh.


class Object(BaseMesh):
    """
    shape is a dictionnary with the path of every
    shape (mesh) available for the Object actor
    """
    shape = {
        'Sphere': '/Game/Meshes/Sphere.Sphere',
        'Cube': '/Game/Meshes/Cube.Cube',
        'Cone': '/Game/Meshes/Cone.Cone',
        'Cylinder': '/Game/Meshes/Cylinder.Cylinder'
    }

    def __init__(self, world=None, params=ObjectParams()):
        if world is not None:
            super().__init__(
                world.actor_spawn(ue.load_class('/Game/Object.Object_C')))
            self.get_parameters(params)
            self.set_parameters()
        else:
            super().__init__()

    def get_parameters(self, params):
        # adjust the location.z to be placed at the bottom of the mesh
        # (by default the pivot is on the middle), mesh is 100x100x100
        params.location.z += 50 * params.scale.z
        super().get_parameters(
            params.location,
            params.rotation,
            params.scale,
            params.friction,
            params.restitution,
            params.overlap,
            params.warning,
            self.shape[params.mesh])
        self.material = ue.load_object(Material, params.material)
        self.mass = params.mass
        self.force = params.force

    def set_parameters(self):
        super().set_parameters()
        self.set_mass(self.mass)
        self.set_force(self.force)
        self.get_mesh().set_simulate_physics()
        print(self.shape)
        print(self.location)

    """
    set the mass of the mesh
    to be honnest I don't really know what the second line do
    """
    def set_mass(self, mass):
        self.mass = mass
        self.mesh.SetMassScale(
            BoneName='None',
            InMassScale=self.mass / self.mesh.GetMassScale())

    """
    If set to True, persistent will make the force apply to the object at
    every tick
    """
    def set_force(self, force, persistent=False):
        if (persistent):
            self.force = force
        self.get_mesh().add_force(force)

    """
    Apply force to the mesh
    """
    def move(self):
        self.get_mesh().add_force(self.force)

    def get_status(self):
        status = super().get_status()
        status['material'] = self.material.get_name()
        status['mass'] = self.mass
        status['force'] = as_dict(self.force)
        return status
