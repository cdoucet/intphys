"""Main script interacting at world level with UE

This module is attached to the MainPythonComponant within the level
blueprint in UE.

"""

import json
import os
import random
import sys

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import KismetSystemLibrary, GameplayStatics
# from unreal_engine.classes import testScreenshot
# from unreal_engine.structs import IntSize

# import screenshot


# the default screen resolution (in pixels)
width, height = 288, 288


ue.log('#' * 50)
ue.log('Beginning new game')
ue.log('#' * 50)
ue.log('Python executable: {}'.format(sys.executable))
ue.log('Python version: {}'.format(sys.version.replace('\n', ', ')))
ue.log('Python path: {}'.format(', '.join(sys.path)))
ue.log('#' * 50)


uclass = {
    'Camera': ue.load_class('/Game/Camera.Camera_C'),
    'Floor': ue.load_class('/Game/Floor.Floor_C'),
    'PhysicsObject': ue.load_class('/Game/PhysicsObject.PhysicsObject_C')
}


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

    def load_scenes(self):
        try:
            scenes_file = os.environ['INTPHYS_SCENES']
        except KeyError:
            self.exit_ue('fatal error, INTPHYS_SCENES not defined, exiting')
            return

        scene_raw = json.loads(open(scenes_file, 'r').read())

    def init_viewport(self, camera):
        """Attach the viewport to the camera

        This initialization was present in the intphys-1.0 blueprint
        but seems to be useless in UE-4.17. This is maybe done by
        default.

        """
        player_controller = GameplayStatics.GetPlayerController(self.world, 0)
        player_controller.SetViewTargetWithBlend(NewViewTarget=camera)

    def exit_ue(self, message=None):
        """Quit the game, optionally displaying an error message"""
        if message:
            ue.log_error(message)

        KismetSystemLibrary.QuitGame(self.world)

    def begin_play(self):
        self.world = self.uobject.get_world()
        ue.log('Raising new world {}'.format(self.world.get_name()))

        self.init_random_seed()
        self.init_resolution()

        # scenes = self.load_scenes()

        # spawn the camera and attach the viewport to it
        camera = self.world.actor_spawn(uclass['Camera'])
        self.init_viewport(camera)

        # spawn the floor
        floor = self.world.actor_spawn(uclass['Floor'])

        # spawn a new PyActor
        new_actor = self.world.actor_spawn(
            uclass['PhysicsObject'],
            FVector(300, 0, 100),
            FRotator(0, 0, 0))

        # add a sphere component as the root one
        static_mesh = new_actor.add_actor_root_component(
            ue.find_class('StaticMeshComponent'), 'SphereMesh')
        ue.log(static_mesh)
