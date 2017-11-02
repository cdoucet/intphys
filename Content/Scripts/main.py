"""Main script interacting at world level with UE

This module is attached to the MainPythonComponant within the level
blueprint in UE.

"""

import json
import os
import random

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import KismetSystemLibrary, GameplayStatics
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize

import screenshot


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

        ue.log('init random numbers generator{}'.format(
            '' if seed is None else ', seed is {}'.format(seed)))

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
            self.exit_ue('fatal error, INTPHYS_CONFIG not defined, exiting')
            return

        config = json.loads(open(config_file, 'r').read())

    def init_viewport(self):
        """Attach the viewport to the camera

        This initialization was present in the intphys-1.0 blueprint
        but seems to be useless in UE-4.17. This is maybe done by
        default.

        """
        player_controller = GameplayStatics.GetPlayerController(self.world, 0)
        camera = ue.find_object(
            '/Game/UEDPIE_0_TestMap.TestMap:PersistentLevel.Camera_81')
        player_controller.SetViewTargetWithBlend(NewViewTarget=camera)

    def exit_ue(self, message=None):
        """Quit the game, optionally displaying an error message"""
        if message:
            ue.log_error(message)

        KismetSystemLibrary.QuitGame(self.world)

    def begin_play(self):
        self.world = self.uobject.get_world()
        ue.log('Raising new world {}'.format(self.world.get_name()))

        self.init_viewport()
        self.init_random_seed()
        self.init_resolution()
        self.init_config_file()

        # spawn a new PyActor
        new_actor = self.world.actor_spawn(
            uclass['PhysicsObject'],
            FVector(300, 0, 100),
            FRotator(0, 0, 0))

        # array = []
        # array.append(new_actor)
        # array2 = []
        # camera = testScreenshot.GetCamera(self.world)
        # camera = ue.find_object('/Game/UEDPIE_0_TestMap.TestMap:PersistentLevel.Camera_81')
        # #screenshot.doTheWholeStuff(IntSize(288, 288), 1, camera, array, array2)
        screenshot.salut()

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
