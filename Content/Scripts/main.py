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

import configuration
from screenshot import Screenshot
from tick import Tick

# the default screen resolution (in pixels)
width, height = 288, 288


# ue.log('#' * 50)
# ue.log('Beginning new game')
# ue.log('#' * 50)
# ue.log('Python executable: {}'.format(sys.executable))
# ue.log('Python version: {}'.format(sys.version.replace('\n', ', ')))
# ue.log('Python path: {}'.format(', '.join(sys.path)))
# ue.log('#' * 50)


# the list of blueprint classes with an attached Python component
# (declared in the editor)
uclass = {
    'Camera': ue.load_class('/Game/Camera.Camera_C'),
    'Floor': ue.load_class('/Game/Floor.Floor_C'),
    'Object': ue.load_class('/Game/Object.Object_C'),
    'Wall': ue.load_class('/Game/Wall.Wall_C')
}


class MainPythonComponant:
    # def __init__(self):
    #     self.world = None
    #     self.ticker = None
    #     self.screenshot = None

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

    def init_configuration(self):
        try:
            json_file = os.environ['INTPHYS_CONFIG']
        except KeyError:
            self.exit_ue(
                'fatal error, INTPHYS_CONFIG not defined, exiting')
        ue.log('loading configuration from {}'.format(json_file))

        try:
            output_dir = os.environ['INTPHYS_DATADIR']
        except KeyError:
            self.exit_ue(
                'fatal error, INTPHYS_DATADIR not defined, exiting')
        ue.log('writing data to {}'.format(output_dir))

        config = configuration.Configuration(json_file, output_dir)

        ue.log('generation of {nscenes} scenes ({ntest} for test and '
               '{ntrain} for train), total of {niterations} iterations'.format(
            nscenes=config.nruns_test + config.nruns_train,
            ntest=config.nruns_test,
            ntrain=config.nruns_train,
            niterations=len(config.iterations)))

    # def load_scenes(self):
    #     try:
    #         scenes_file = os.environ['INTPHYS_SCENES']
    #     except KeyError:
    #         self.exit_ue('fatal error, INTPHYS_SCENES not defined, exiting')
    #         return
    #     scene_raw = json.loads(open(scenes_file, 'r').read())

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
        ue.log('Raising up new world {}'.format(self.world.get_name()))

        # init the seed for random parameters generation
        self.init_random_seed()

        # init the rendering resolution
        self.init_resolution()

        # spawn the camera and attach the viewport to it
        camera = self.world.actor_spawn(uclass['Camera'])
        self.init_viewport(camera)

        camera_pos = camera.get_actor_location()
        ue.log('camera position is {}'.format(camera_pos))

        # init the configuration
        # config = self.init_configuration()
        # scenes = [{'block': 'block_O1.train', 'path': '/tmp/train/01_block_O1_train', 'type': -1, 'id': 1}]
        # for scene_params in scenes:
        #     scene = Scene(camera, scene_params)

        # spawn the floor
        floor = self.world.actor_spawn(uclass['Floor'])

        # spawn an actor
        self.actor = self.world.actor_spawn(uclass['Object'])

        # setup the sceenshots
        self.screenshot = Screenshot(width, height, camera)
        output_dir = os.path.abspath('./screenshots')

        # register the tick for taking screenshots
        # self.ticker = Tick()
        self.ticker = Tick(nticks=1)

        self.ticker.add_hook(self.screenshot.capture, 'slow')
        self.ticker.add_hook(lambda: self.screenshot.save(output_dir), 'final')
        self.ticker.add_hook(self.exit_ue, 'final')

        # run the scene
        self.ticker.run()

    def tick(self, dt):
        self.ticker.tick(dt)
