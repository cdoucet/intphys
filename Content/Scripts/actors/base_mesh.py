# coding: utf-8

import unreal_engine as ue
import random
from magical_value import MAGICAL_VALUE
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from actors.base_actor import BaseActor

from unreal_engine.classes import Friction

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
BaseMesh inherits from BaseActor.
It is the base class of every python component build with a mesh.
"""

class BaseMesh(BaseActor):
    """
    __init__ instantiate the class
    parameters ->
    actor: spawned actor (UObject)
    mesh_str: the path of the mesh/shape of the actor (str). Default value: a sphere
    location: location of the actor (FVector). Default value: 0, 0, 0
    rotation: rotation of the actor (FRotator). Default value: 0, 0, 0
    material: material of the actor (UObject). Default value: a random one in the relevant directory
    scale: scale of the actor (FVector). Default value: 1, 1, 1
    mass: mass of the actor (float). Default value: 1.0
    force: force applied to the actor (FVector) Default value: 0.0, 0.0, 0.0
    """
    def __init__(self, actor = None):
        if (actor != None):
            super().__init__(actor)
        else:
            super().__init__()

    def get_parameters(self, location, rotation, scale, friction, manage_hits, mesh_str):
        super().get_parameters(location, rotation, manage_hits)
        self.scale = scale
        if (friction == MAGICAL_VALUE):
            self.friction = random.uniform(-1000, 1000)
        else:
            self.friction = friction
        self.mesh_str = mesh_str

    def set_parameters(self):
        super().set_parameters()
        self.set_location(self.location)
        self.set_rotation(self.rotation)
        self.set_mesh()
        self.set_friction(self.friction)
        if (self.manage_hits == True):
            self.mesh.call('SetCollisionProfileName BlockAll')
        
    """
    set_mesh sets the mesh, enable collision, set the material and the scale
    """
    def set_mesh(self):
        self.mesh = self.get_actor().get_actor_component_by_type(ue.find_class('StaticMeshComponent'))
        # enable collisions
        #self.mesh.call('SetCollisionProfileName BlockAll')
        #self.actor.SetActorEnableCollision(True)

        # setup mesh and material
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))
        self.mesh.set_material(0, self.material)
        self.actor.set_actor_scale(self.scale)

    def get_mesh(self):
        return self.get_actor().get_actor_component_by_type(ue.find_class('StaticMeshComponent'))

    """
    set_mesh_str change the current mesh by another
    """
    def set_mesh_str(self, mesh_str):
        self.mesh_str = mesh_str
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))

    def get_mesh_str(self):
        return self.mesh_str

    def set_material(self, material_str):
        self.material = ue.load_object(Material, material_str)
        self.mesh.set_material(0, self.material)

    def get_material(self):
        return self.material

    def set_scale(self, scale):
        self.scale = scale
        self.actor.set_actor_scale(self.scale)

    def get_scale(self):
        return self.scale

    def get_friction(self):
        return self.friction

    def set_friction(self, friction):
        self.friction = friction
        Friction.SetFriction(self.material, friction)

    """
    begin_play is called when actor_spawn is called.
    It is a kind of second __init__, for the python component
    """
    def begin_play(self):
        self.set_actor(self.uobject.get_owner())
        # ue.log('begin play {}'.format(self.actor.get_name()))

    def get_status(self):
        status = super().get_status()
        status['scale'].append(('x', self.scale.x))
        status['scale'].append(('y', self.scale.y))
        status['scale'].append(('z', self.scale.z))
        status['friction'] = self.friction
        status['mesh_str'] = self.mesh_str
        return status
