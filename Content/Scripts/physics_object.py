"""Physics objects are the scene's objects submited to physics

This is the Python componant of the PhysicsObject blueprint class.

A physics object has a mesh (3D shape), a material (texture), a mass.

"""

import unreal_engine as ue

from unreal_engine import FVector


class PhysicsObject:
    def __init__(self):
        self.mesh_name = '/Engine/EngineMeshes/Sphere.Sphere'
        self.material_name = None
        self.mass = 1.0
        self.force = FVector(-1e7, 0.0, 0.0)

        self.total_time = 0

    def begin_play(self):
        # retrieve the actor (here we are in componant)
        self.actor = self.uobject.get_owner()

        # retrieve
        self.mesh = self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))

        # setup mesh and material TODO get them random
        self.mesh.call('SetStaticMesh {}'.format(self.mesh_name))
        self.mesh.call('SetMaterial {}'.format(self.material_name))

        # setup mass
        self.mesh.SetMassScale(
            BoneName='None',
            InMassScale=self.mass/self.mesh.GetMassScale())

        # setup force
        self.mesh.add_force(self.force)

        ue.log('{} begin play at {}{}'.format(
            self.actor.get_name(),
            self.actor.get_actor_location(),
            self.actor.get_actor_rotation()))

    def tick(self, delta_time):
        self.total_time += delta_time
        done = 0

        # if self.total_time >= 1 and done < 1:
        #     self.actor.SetActorHiddenInGame(True)
        #     done = 1
        # if self.total_time >=2 and done < 2:
        #     self.mesh.call('SetStaticMesh /Engine/EngineMeshes/Cube.Cube')
        #     self.actor.SetActorHiddenInGame(False)
        #     done = 2

    def on_actor_hit(self, me, other, normal_impulse, hit_result):
        message = 'actor overlaping {}'.format(other.get_name())
        ue.log(message)

    def on_actor_begin_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps the camera"""
        message = 'Camera overlaping {}'.format(other.get_name())
        ue.log(message)
        # ue.log_error(message)
        # raise RuntimeError(message)
