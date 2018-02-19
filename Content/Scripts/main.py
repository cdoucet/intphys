import json
import os
import random

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary
from tools.scheduler import Scheduler
from tools.utils import exit_ue


# the default game resolution, for both scene rendering and saved
# images (width * height in pixels)
DEFAULT_RESOLUTION = (288, 288)


class Main:
    def begin_play(self):
        # get the world from the attached component
        world = self.uobject.get_world()

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

        # setup the scheduler with the list of scenes to generate
        self.scheduler = Scheduler(world, scenes_json, output_dir)

    def tick(self, dt):
        # delegate ticks to the scheduler
        self.scheduler.tick(dt)


    # camera = Camera(self.world, FVector(0, 0, 150), FRotator(0, -5, 0))
    # self.init_capture(output_dir, camera)
    # floor = Floor(self.world, FVector(10, 10, 1), "/Game/Materials/Floor/M_Ground_Gravel")
    # object_1 = Object(
    #     self.world, Object.shape['Cube'],
    #     FVector(300, 0, 200), FRotator(0, 0, 45), FVector(1, 1, 1),
    #     "/Game/Materials/Actor/M_Metal_Steel")
    # object2 = Object(self.world, Object.shape['Cube'],
    #                  FVector(-1000, 0, 150), FRotator(0, 0, 45), FVector(1, 1, 1),
    #                  "/Game/Materials/Object/GreenMaterial")
    # wall_front = Wall(self.world, 'Front', FVector(10, 1, 5))
    # wall_left = Wall(self.world, 'Left', FVector(10, 1, 5))
    # wall_right = Wall(self.world, 'Right', FVector(10, 1, 5))
    # occluder = Occluder(
    #     self.world,
    #     FVector(1000, 0, 150), FRotator(0, 0, 0), FVector(1, 1, 1),
    #     "/Game/Materials/Object/GreenMaterial")

    # from unreal_engine.classes import Screenshot
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
