import os
import random

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary

from tools.utils import parse_scenes_json, exit_ue
from tools.director import Director

# the default game resolution, for both scene rendering and saved
# images (width * height in pixels)
DEFAULT_RESOLUTION = ("288", "288")

class Main:
    def begin_play(self):
        # get the world from the attached component
        world = self.uobject.get_world()

        # load the specifications of scenes we are going to generate
        try:
            scenes_json = os.environ['INTPHYS_SCENES']
        except KeyError:
            exit_ue(world, 'fatal error, INTPHYS_SCENES not defined, exiting')

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
            output_dir = None
            ue.log_warning('INTPHYS_OUTPUTDIR not defined, capture disabled')

        # setup the director with the list of scenes to generate
        scenes = parse_scenes_json(world, scenes_json)
        size = (resolution[0], resolution[1], 100)
        self.director = Director(world, scenes, size, output_dir)

    def tick(self, dt):
        # delegate ticking to the director
        self.director.tick(dt)
