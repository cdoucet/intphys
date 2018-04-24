# coding: utf-8

import unreal_engine as ue
from unreal_engine.classes import Material, StaticMesh, Friction

from actors.base_actor import BaseActor
from tools.utils import as_dict


"""
Ok here we go:
This is a recursive instantiate class.
The general principle is to instantiate a class
twice to avoid making two distinct classes.
I needed to instantiate a python component with
parameters but UnrealEnginePython
wouldn't let me do that.
Furthermore, I couldn't spawn the actor without instanciate the class and thus,
I couldn't spawn it with any parameter.

Let me explain myself :
In the main, I call the constructor of the class Object
(for instance, or Floor, or Occluder),
which call the __init__ function of Object with at least 1 argument, world
which call the __init__function of BaseMesh with at least
1 argument, mesh_str.
In the Object __init__ function, I call actor_spawn,
which implicitely instanciate Object (yes, again)
BUT during the second instantiation, no parameters is given to __init__
(of Object and BaseMesh)
(this is why there is default values to every parameters of __init__).
Thus, if __init__ is called without any parameters,
I know that it is the second instantiation,
so I don't spawn the actor again.
Once the object spawned, all I have to do is to set
the parameters in the second instantiation
(location, rotation,...).
"""

"""
BaseMesh inherits from BaseActor.
It is the base class of every python component build with a mesh.
"""


class BaseMesh(BaseActor):
    def __init__(self, actor=None):
        if actor is not None:
            super().__init__(actor)
        else:
            super().__init__()

    def get_parameters(self, location, rotation,
                       scale, friction, restitution,
                       overlap, warning, mesh_str):
        super().get_parameters(location, rotation, overlap, warning)
        self.scale = scale
        self.friction = friction
        self.restitution = restitution
        self.mesh_str = mesh_str

    def set_parameters(self):
        super().set_parameters()
        self.set_mesh()
        self.set_scale(self.scale)
        self.set_friction(self.friction)
        self.set_restitution(self.restitution)
        if self.overlap is False:
            self.mesh.call('SetCollisionProfileName BlockAll')

    """
    set_mesh sets the mesh, enable collision, set the material
    """
    def set_mesh(self):
        self.mesh = self.get_actor().get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))
        # setup mesh and material
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))
        self.mesh.set_material(0, self.material)

    def get_mesh(self):
        return self.get_actor().get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))

    """
    set_mesh_str change the current mesh by another
    """
    def set_mesh_str(self, mesh_str):
        self.mesh_str = mesh_str
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))

    def set_material(self, material_str):
        self.material = ue.load_object(Material, material_str)
        self.mesh.set_material(0, self.material)

    def set_scale(self, scale):
        self.scale = scale
        self.actor.set_actor_scale(self.scale)

    def set_friction(self, friction):
        self.friction = friction
        Friction.SetFriction(self.material, friction)

    def set_restitution(self, restitution):
        self.restitution = restitution
        Friction.SetRestitution(self.material, restitution)

    """
    begin_play is called when actor_spawn is called.
    It is a kind of second __init__, for the python component
    """
    def begin_play(self):
        self.set_actor(self.uobject.get_owner())
        # ue.log('begin play {}'.format(self.actor.get_name()))

    def get_status(self):
        status = super().get_status()
        status['scale'] = as_dict(self.scale)
        status['friction'] = self.friction
        status['restitution'] = self.restitution
        status['mesh'] = self.mesh_str
        return status
