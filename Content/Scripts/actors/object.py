"""Physics objects are the scene's objects submited to physics

This is the Python componant of the PhysicsObject blueprint class.

A physics object is defined by a mesh (3D shape), a material (texture)
and a mass. It obeys to physical laws. It can be spawn at any location
in the world and a force vector can be applied to it.

"""

# import numpy as np
import unreal_engine as ue

from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

from actors.abstract_actor import BaseActor
from materials import load_materials, get_random_material


class Object(BaseActor):
    object_materials = load_materials('Materials/Actor')

    def __init__(self):
        super(Object, self).__init__()

        self.params = {
            'mesh': '/Game/Meshes/Sphere',
            'material': get_random_material(self.object_materials),
            'mass': 1.0,
            'force': FVector(-1e2, 0.0, 0.0),
            'location': FVector(0, -100, 0),
            'rotation': FRotator(0, 0, 0),

        }

    def begin_play(self):
        super(Object, self).begin_play()

        self.get_mesh().SetMassScale(
            BoneName='None',
            InMassScale=self.params['mass'] / self.get_mesh().GetMassScale())

    def activate_physics(self):
        self.get_mesh().set_simulate_physics()

        if 'force' in self.params:
            self.get_mesh().add_force(self.params['force'])

    # def tick(self, delta_time):
    #     self.total_time += delta_time
    #     done = 0
    #     if self.total_time >= 2 and done < 1:
    #         self.actor.SetActorHiddenInGame(True)
    #         done = 1
    #     if self.total_time >= 3 and done < 2:
    #         self.actor.set_actor_scale(0.1, 0.1, 0.1)
    #         # self.mesh.SetStaticMesh(
    #         #     ue.load_object(StaticMesh, '/Engine/EngineMeshes/Cube.Cube'))
    #         self.actor.SetActorHiddenInGame(False)
    #         done = 2


    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps this object"""
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log(message)
