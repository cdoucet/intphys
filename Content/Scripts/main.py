import importlib
import json
import os
import random
import shutil
import sys
import math

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary, GameplayStatics
from unreal_engine import FVector, FRotator

from unreal_engine.classes import Screenshot

from actors.object import Object
from actors.camera import Camera
from actors.floor import Floor
from actors.wall import Wall
from actors.occluder import Occluder
from tools.tick import Tick
#from tools.screenshot import Screenshot

# the default screen resolution (in pixels)
width, height = 288, 288

class Main:
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
            self.uobject.get_world(), 'r.SetRes {}'.format(resolution))

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
        camera = Camera(self.world, FVector(0, 0, 150), FRotator(0, -5, 0))
        ue.log('camera position is {}'.format(camera.location))

        # init the configuration
        # config = self.init_configuration()
        # scenes = [{'block': 'block_O1.train', 'path': '/tmp/train/01_block_O1_train', 'type': -1, 'id': 1}]
        # for scene_params in scenes:
        #     scene = Scene(camera, scene_params)

        # spawn an actor
        floor = Floor(self.world, FVector(10, 10, 1), "/Game/Materials/Floor/M_Ground_Gravel")

        object_1 = Object(
            self.world, Object.shape['Cube'],
            FVector(300, 0, 200), FRotator(0, 0, 45), FVector(1, 1, 1),
            "/Game/Materials/Actor/M_Metal_Steel")

        # #object2 = Object(self.world, Object.shape['Cube'], FVector(-1000, 0, 150), FRotator(0, 0, 45), FVector(1, 1, 1), "/Game/Materials/Object/GreenMaterial")

        # wall_front = Wall(self.world, 'Front', FVector(10, 1, 5))
        # wall_left = Wall(self.world, 'Left', FVector(10, 1, 5))
        # wall_right = Wall(self.world, 'Right', FVector(10, 1, 5))

        # occluder = Occluder(
        #     self.world,
        #     FVector(1000, 0, 150), FRotator(0, 0, 0), FVector(1, 1, 1),
        #     "/Game/Materials/Object/GreenMaterial")

        # setup the sceenshots
        output_dir = os.path.abspath('./screenshots')
        # delete the dir if existing
        if os.path.isdir(output_dir):
            ue.log('overwrite {}'.format(output_dir))
            shutil.rmtree(output_dir)

        # self.screenshot = Screenshot(output_dir, (100, width, height), camera.get_actor())
        Screenshot.Initialize(output_dir, width, height, 100, camera.get_actor(), True)

        # register the tick for taking screenshots
        # self.ticker = Tick()
        self.ticker = Tick(nticks=100)
        self.ticker.add_hook(Screenshot.Capture, 'slow')
        # self.ticker.add_hook(self.screenshot.capture, 'slow')
        self.ticker.add_hook(Screenshot.Save, 'final')
        self.ticker.add_hook(self.exit_ue, 'final')

        # run the scene
        self.ticker.run()

    def tick(self, dt):
        self.ticker.tick(dt)
