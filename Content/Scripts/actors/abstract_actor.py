"""Common ancestor to all the actors"""

import unreal_engine as ue

from unreal_engine import FVector
from unreal_engine.classes import Material, StaticMesh


class BaseActor(object):
    def __init__(self):
        self.params = {
            'mesh': None,
            'material': None,
            'location': FVector(0, 0, 0),
            'rotation': FVector(0, 0, 0),
            'scale': FVector(1, 1, 1)
        }

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
        mesh.SetStaticMesh(ue.load_object(StaticMesh, self.params['mesh']))
        # mesh.set_material(0, ue.load_object(Material, self.params['material']))
        mesh.set_material(0, self.params['material'])

        # setup position
        actor.set_actor_location(self.params['location'])
        actor.set_actor_rotation(self.params['rotation'])
        actor.set_actor_scale(self.params['scale'])


    def manage_overlap(self, me, other):
        pass
