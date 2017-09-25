"""Main script interacting at world level with UE

This module is attached to the MainPythonComponant PyActor in UE.

"""

import unreal_engine as ue
import mobile_object

import os
import png

from unreal_engine import FVector, FRotator
from unreal_engine.classes import Actor


# the default screen resolution (in pixels)
width, height = 288, 288


ue.log('#' * 50)
ue.log('Beginning new game')


class MainPythonComponant:
    def get_x_resolution(self):
        return str(width)

    def get_y_resolution(self):
        return str(height)

    def print_tick(self, delta_seconds):
        ue.log('ticking after {}'.format(float(delta_seconds)))
        print(ue.get_viewport_screenshot() == None)

    def begin_play(self):
        self.world = self.uobject.get_world()
        ue.log('Raising new world {}'.format(self.world))

        # TODO spawn actors from here

        # actor_class = ue.find_object('PysicsObject')
        # ue.log('new actor class is {}'.format(actor_class))

        # # spawn a new PyActor
        # new_actor = self.world.actor_spawn(
        #     Actor,
        #     FVector(100, 0, 50),
        #     FRotator(0, 0, 0))

        # # add a sphere component as the root one
        # static_mesh = new_actor.add_actor_root_component(
        #     ue.find_class('StaticMeshComponent'), 'SphereMesh')
        # ue.log(static_mesh)

        # # set the mesh as the Sphere asset
        # static_mesh.call('SetStaticMesh /Engine/EngineMeshes/Sphere.Sphere')
        # # # set the python module
        # # new_actor.set_property('PythonModule', 'mobile_object')
        # # # set the python class
        # # new_actor.set_property('PythonClass', 'MobileObjectPythonComponant')

        # new_actor.bVisible = True
