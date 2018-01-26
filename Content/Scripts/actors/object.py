import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseActor import BaseActor

# Ok here we go:
# This is a recursive instantiate class. Let me explain myself :
# In the main, I call the constructor of the class Object,
# which call the __init__ function of Object with 3 arguments : world, location and rotation
# In the __init__ function, I call actor_spawn, which implicitely instanciate Object (yes, again)
# BUT during the second instantiation, no parameters is given to __init__
# (this is why there is default values to every parameters of __init__)
# Thus, if __init__ is called without "world" parameter, I know that it is the second instantiation,
# which purpose is to spawn the object in the world
# Once the object spawned, all I have to do is to set the parameters in the second instantiation
# (location, rotation,...)
# et voilà !

class Object(BaseActor):
    def __init__(self, world = None, location = FVector(0, 0, 0), rotation = FRotator(0, 0, 0)):
        self.mesh = '/Engine/EngineMeshes/Sphere.Sphere'
        self.material = None
        self.scale = FVector(1, 1, 1)
        self.mass = 1.0
        self.force = FVector(-1e2, 0.0, 0.0)
        self.set_actor(None)
        if (world != None):
            self.set_actor(world.actor_spawn(ue.load_class('/Game/Object.Object_C')))
            # self.amIComponentb = False
            self.set_location(location)
            self.set_rotation(rotation)
            
        BaseActor.__init__(self, self.actor, location, rotation)
        #else:
        #    self.amIComponentb = True
    
    def get_mesh(self):
        """retrieve the StaticMeshComponent of the actor"""
        return self.get_actor().get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))

    def begin_play(self):
        self.set_actor(self.uobject.get_owner())
        mesh = self.get_mesh()
        ue.log('begin play {}'.format(self.actor.get_name()))

        # manage OnActorBeginOverlap events
        self.actor.bind_event('OnActorBeginOverlap', self.manage_overlap)

        # enable collisions
        mesh.call('SetCollisionProfileName BlockAll')
        self.actor.SetActorEnableCollision(True)

        # setup mesh and material
        mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh))
        #mesh.set_material(0, ue.load_object(Material, self.material))

        # setup position
        self.actor.set_actor_location(self.location)
        self.actor.set_actor_rotation(self.rotation)
        self.actor.set_actor_scale(self.scale)

        self.get_mesh().SetMassScale(
            BoneName='None',
            InMassScale=self.mass / self.get_mesh().GetMassScale())

    def activate_physics(self):
        self.get_mesh().set_simulate_physics()

        if 'force' in self.params:
            self.get_mesh().add_force(self.force)

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps this object"""
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log(message)
