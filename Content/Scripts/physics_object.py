"""Physics objects are the scene's objects submited to physics

This is the Python componant of the PhysicsObject blueprint class.

A physics object is defined by a mesh (3D shape), a material (texture)
and a mass. It obeys to physical laws. It can be spawn at any location
in the world and a force vector can be applied to it.

"""

import numpy as np
import unreal_engine as ue

from unreal_engine import FVector
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel


class PhysicsObject:
    def __init__(self):
        ue.log('init PhysicsObject')

        # TODO mesh and material as uobjects, not strings
        self.parameters = {
            'mesh': '/Game/Meshes/Sphere.Sphere',
            'material': '/Game/Materials/Actor/M_Tech_Panel.M_Tech_Panel',
            'mass': 1.0,
            'force': FVector(-1e5, 0.0, 0.0)
        }

        self.materials = ue.get_assets('/Game/Materials/Actor')
        self.total_time = 0

    def begin_play(self):
        # retrieve the actor from its Python component
        self.actor = self.uobject.get_owner()

        # manage OnActorBeginOverlap events
        self.actor.bind_event('OnActorBeginOverlap', self.manage_overlap)

        # retrieve the actor's mesh component
        self.mesh = self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))

        # setup physics
        self.mesh.call('SetCollisionProfileName BlockAll')
        # TODO not sure it works nor its usefull...
        self.mesh.SetCollisionObjectType(
            Channel=np.uint8(ECollisionChannel.PhysicsBody))
        self.actor.SetActorEnableCollision(True)
        self.mesh.set_simulate_physics()

        # setup mesh, material, mass and force from parameters
        self.mesh.SetStaticMesh(
            ue.load_object(StaticMesh, self.parameters['mesh']))

        self.mesh.set_material(
            0, ue.load_object(Material, self.parameters['material']))

        self.mesh.SetMassScale(
            BoneName='None',
            InMassScale=self.parameters['mass'] / self.mesh.GetMassScale())

        self.mesh.add_force(self.parameters['force'])

        ue.log('begin play {}'.format(self.actor.get_name()))

    # def tick(self, delta_time):
    #     self.total_time += delta_time
    #     done = 0

    #     if self.total_time >= 1 and done < 1:
    #         self.actor.SetActorHiddenInGame(True)
    #         done = 1
    #     if self.total_time >= 2 and done < 2:
    #         self.mesh.SetStaticMesh(
    #             ue.load_object(StaticMesh, '/Engine/EngineMeshes/Cube.Cube'))
    #         self.actor.SetActorHiddenInGame(False)
    #         done = 2

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps the camera"""
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log(message)
