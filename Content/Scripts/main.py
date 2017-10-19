"""Main script interacting at world level with UE

This module is attached to the MainPythonComponant within the level
blueprint in UE.

"""

import json
import os
import random

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import KismetSystemLibrary


# the default screen resolution (in pixels)
width, height = 288, 288


ue.log('#' * 50)
ue.log('Beginning new game')


uclass = {
    'PhysicsObject': ue.load_class('/Game/PhysicsObject.PhysicsObject_C')}


class MainPythonComponant:
    def init_random_seed(self):
        # init random number generator with a seed
        try:
            seed = os.environ['INTPHYS_SEED']
        except KeyError:
            seed = None
        ue.log('init random numbers generator, seed is {}'.format(seed))
        random.seed(seed)

    def init_resolution(self):
        try:
            resolution = os.environ['INTPHYS_RESOLUTION']
        except KeyError:
            resolution = str(width) + 'x' + str(height)
            ue.log('INTPHYS_RESOLUTION not defined, using default')

        ue.log('set screen resolution to {}'.format(resolution))
        KismetSystemLibrary.ExecuteConsoleCommand(
            self.uobject.get_world(),
            'r.SetRes {}'.format(resolution))

    def init_config_file(self):
        try:
            config_file = os.environ['INTPHYS_CONFIG']
        except KeyError:
            ue.log_error('fatal error, INTPHYS_CONFIG not defined, exiting')
            self.exit_ue()
            return

        config = json.loads(open(config_file, 'r'))
        ue.log('configuration parsed is : {}'.format(json.dumps(config)))


    def exit_ue(self):
        KismetSystemLibrary.QuitGame(self.world)

    def begin_play(self):
        self.world = self.uobject.get_world()
        ue.log('Raising new world {}'.format(self.world.get_name()))

        self.init_random_seed()
        self.init_resolution()
        self.init_config_file()

        # # spawn a new PyActor
        # new_actor = self.world.actor_spawn(
        #     uclass['PhysicsObject'],
        #     FVector(300, 0, 100),
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
