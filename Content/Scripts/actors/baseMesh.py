import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseActor import BaseActor

"""
Ok here we go:
This is a recursive instantiate class. Let me explain myself :
In the main, I call the constructor of the class Object,
which call the __init__ function of Object with 3 arguments : world, location and rotation
In the __init__ function, I call actor_spawn, which implicitely instanciate Object (yes, again)
BUT during the second instantiation, no parameters is given to __init__
(this is why there is default values to every parameters of __init__)
Thus, if __init__ is called without "world" parameter, I know that it is the second instantiation,
which purpose is to spawn the object in the world
Once the object spawned, all I have to do is to set the parameters in the second instantiation
(location, rotation,...)
et voilà !
"""

class BaseMesh(BaseActor):
    def __init__(self, actor = None, mesh_str = None, location = FVector(0, 0, 0), rotation = FRotator(0, 0, 0), material = None, scale = FVector(1, 1, 1), mass = 1.0, force = FVector(-1e2, 0.0, 0.0)):
        self.mesh_str = mesh_str
        self.material = material
        self.scale = scale
        self.mass = mass
        self.force = force
        if (mesh_str != None):
            BaseActor.__init__(self, actor, location, rotation)
            self.set_location(location)
            self.set_rotation(rotation)
            self.set_mesh(mesh_str)
        else:
            BaseActor.__init__(self)

    def set_mesh(self, mesh_str):
        self.mesh = self.get_actor().get_actor_component_by_type(ue.find_class('StaticMeshComponent'))
        # enable collisions
        self.mesh.call('SetCollisionProfileName BlockAll')
        self.actor.SetActorEnableCollision(True)

        # setup mesh and material
        self.mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh_str))
        self.mesh.set_material(0, ue.load_object(Material, self.material[0]))
        self.actor.set_actor_scale(self.scale)
        # Got an error when uncommenting this
        """
        self.mesh.SetMassScale(
            BoneName='None',
            InMassScale=self.mass / self.mesh.GetMassScale())
        """

    def get_mesh(self):
        #"""retrieve the StaticMeshComponent of the actor"""
        #return self.get_actor().get_actor_component_by_type(
        #    ue.find_class('StaticMeshComponent'))
        return self.mesh

    def begin_play(self):
        self.set_actor(self.uobject.get_owner())
        ue.log('begin play {}'.format(self.actor.get_name()))

        # manage OnActorBeginOverlap events
        self.actor.bind_event('OnActorBeginOverlap', self.manage_overlap)

        # setup position
        self.actor.set_actor_location(self.location)
        self.actor.set_actor_rotation(self.rotation)

    def activate_physics(self):
        self.get_mesh().set_simulate_physics()

        if 'force' in self.params:
            self.get_mesh().add_force(self.force)
