import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseActor import BaseActor

class Object(BaseActor):
    def get_actor(self):
        """retrieve the actor from its Python component"""
        return self.uobject.get_owner()

    def get_mesh(self):
        """retrieve the StaticMeshComponent of the actor"""
        return self.get_actor().get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))


    def begin_play(self):
        actor = self.get_actor()
        mesh = self.get_mesh()
        ue.log('begin play {}'.format(actor.get_name()))

        # manage OnActorBeginOverlap events
        actor.bind_event('OnActorBeginOverlap', self.manage_overlap)

        # enable collisions
        mesh.call('SetCollisionProfileName BlockAll')
        actor.SetActorEnableCollision(True)

        # setup mesh and material
        mesh.SetStaticMesh(ue.load_object(StaticMesh, self.mesh))
        #mesh.set_material(0, ue.load_object(Material, self.material))

        # setup position
        actor.set_actor_location(self.location)
        actor.set_actor_rotation(self.rotation)
        actor.set_actor_scale(self.scale)

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
