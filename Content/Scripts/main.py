# coding: utf-8

import importlib
import json
import os
import random
import shutil
import sys
import math

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import KismetSystemLibrary, GameplayStatics
from unreal_engine.classes import Screenshot

from actors.object import Object
from actors.camera import Camera
from actors.floor import Floor
from actors.wall import Wall
from actors.occluder import Occluder

from tools.tick import Tick
from tools.configuration import Configuration
from tools.scheduler import Scheduler


# the default game resolution, for both scene rendering and saved
# images (width * height in pixels)
DEFAULT_RESOLUTION = (288, 288)


# TODO Does not exit the game immediately, find better
def exit_ue(world, message=None):
    """Quit the game, optionally displaying an error message"""
    if message:
        ue.log_error(message)
    KismetSystemLibrary.QuitGame(world)
    sys.exit(1 if message else 0)


class Main:
    def begin_play(self):
        # get the world from the attached component
        world = uobject.get_world()

        # init random number generator
        try:
            seed = os.environ['INTPHYS_SEED']
        except KeyError:
            seed = None
        random.seed(seed)

        # setup screen resolution
        try:
            res = os.environ['INTPHYS_RESOLUTION'].split('x')
            resolution = (res[0], res[1])
        except KeyError:
            resolution = DEFAULT_RESOLUTION
        KismetSystemLibrary.ExecuteConsoleCommand(
            world, 'r.SetRes {}'.format('x'.join(resolution)))

        # setup output directory where to save generated data
        try:
            output_dir = os.environ['INTPHYS_OUTPUTDIR']
        except KeyError:
            exit_ue(world, 'fatal error, INTPHYS_OUTPUTDIR not defined, exiting')

        # load the specifications of scenes we are going to generate
        try:
            scenes_config_file = os.environ['INTPHYS_SCENES']
            scenes_json = json.loads(open(scenes_config_file, 'r').read())
        except KeyError:
            exit_ue(world, 'fatal error, INTPHYS_SCENES not defined, exiting')

        self.scheduler = Scheduler(scenes_json, output_dir)
        self.scheduler.run()

    def tick(self, dt):
        self.scheduler.tick(dt)




        # for scene_params in self.scenes_params:
        #     scene = Scene(scene_params)

        #     scene.run()


        # self.ticker = Tick(nticks=100)
        # self.ticker.add_hook(lambda: exit_ue(self.world), 'final')

        # camera = Camera(self.world, FVector(0, 0, 150), FRotator(0, -5, 0))
        # self.init_capture(output_dir, camera)

        # # init the configuration
        # # scenes = [{'block': 'block_O1.train', 'path': '/tmp/train/01_block_O1_train', 'type': -1, 'id': 1}]
        # # for scene_params in scenes:
        # #     scene = Scene(camera, scene_params)

        # # spawn an actor
        # floor = Floor(self.world, FVector(10, 10, 1), "/Game/Materials/Floor/M_Ground_Gravel")

        # object_1 = Object(
        #     self.world, Object.shape['Cube'],
        #     FVector(300, 0, 200), FRotator(0, 0, 45), FVector(1, 1, 1),
        #     "/Game/Materials/Actor/M_Metal_Steel")

        # #object2 = Object(self.world, Object.shape['Cube'], FVector(-1000, 0, 150), FRotator(0, 0, 45), FVector(1, 1, 1), "/Game/Materials/Object/GreenMaterial")

        # wall_front = Wall(self.world, 'Front', FVector(10, 1, 5))
        # wall_left = Wall(self.world, 'Left', FVector(10, 1, 5))
        # wall_right = Wall(self.world, 'Right', FVector(10, 1, 5))

        # occluder = Occluder(
        #     self.world,
        #     FVector(1000, 0, 150), FRotator(0, 0, 0), FVector(1, 1, 1),
        #     "/Game/Materials/Object/GreenMaterial")

    # def init_capture(self, output_dir, camera):
    #     """If not in dry mode, register the screenshot manager for ticking"""
    #     if 'INTPHYS_DRY' in os.environ:
    #         ue.log('Running in dry mode, capture disabled')
    #     else:
    #         ue.log('saving data to {}'.format(output_dir))

    #         # setup the sceenshots
    #         Screenshot.Initialize(width, height, 100, camera.get_actor())

    #         def save_capture():
    #             # TODO retrieve max_depth and masks in get_status()
    #             done, max_depth, masks = Screenshot.Save(output_dir)
    #             Screenshot.reset()
    #             ue.log('max depth is {}'.format(max_depth))
    #             ue.log('masks are {}'.format(masks))

    #         # register for ticking
    #         self.ticker.add_hook(Screenshot.Capture, 'slow')
    #         self.ticker.add_hook(save_capture, 'final')
