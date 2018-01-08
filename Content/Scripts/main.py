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

import configuration
import screenshot
import utils

# the default screen resolution (in pixels)
width, height = 288, 288


ue.log('#' * 50)
ue.log('Beginning new game')
ue.log('#' * 50)
ue.log('Python executable: {}'.format(sys.executable))
ue.log('Python version: {}'.format(sys.version.replace('\n', ', ')))
ue.log('Python path: {}'.format(', '.join(sys.path)))
ue.log('#' * 50)


# the list of blueprint classes with an attached Python component
# (declared in the editor)
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

    def init_configuration(self):
        try:
            json_file = os.environ['INTPHYS_CONFIG']
        except KeyError:
            utils.exit_ue(
                'fatal error, INTPHYS_CONFIG not defined, exiting')
        ue.log('loading configuration from {}'.format(json_file))

        try:
            output_dir = os.environ['INTPHYS_DATADIR']
        except KeyError:
            utils.exit_ue(
                'fatal error, INTPHYS_DATADIR not defined, exiting')
        ue.log('writing data to {}'.format(output_dir))

        config = configuration.Configuration(json_file, output_dir)

        ue.log('generation of {nscenes} scenes ({ntest} for test and '
               '{ntrain} for train), total of {niterations} iterations'.format(
            nscenes=config.nruns_test + config.nruns_train,
            ntest=config.nruns_test,
            ntrain=config.nruns_train,
            niterations=len(config.iterations)))

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
        ue.log('Raising up new world {}'.format(self.world.get_name()))

        # inti the seed for random parameters generation
        self.init_random_seed()

        # init the rendering resolution
        self.init_resolution()

        # init the configuration
        config = self.init_configuration()
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

    def tick(self, delta_time):
        pass

    #def tick(self, delta_time):
        #print delta_time
        # size = IntSize(288, 288) # this line let size.X and size.Y with a null value... can't say why
        # size.X = 288
        # size.Y = 288
        # array = []
        # array.append(new_actor)
        # for o in ue.all_objects():
        #     o.get_full_name()
        # #camera = ue.find_object('/Game/UEDPIE_0_TestMap.TestMap:PersistentLevel.Camera_82')
        # array2 = []
        #if screenshot.doTheWholeStuff(size, 1, camera, array, array2) == False:
            #print "doTheWholeStuff failed"

        #array = []
        #array.append(new_actor)
        #array2 = []
        #camera = testScreenshot.GetCamera(self.world)
        #camera = ue.find_object('/Game/UEDPIE_0_TestMap.TestMap:PersistentLevel.Camera_81')
        #screenshot.doTheWholeStuff(IntSize(288, 288), 1, camera, array, array2)
        #screenshot.salut()
