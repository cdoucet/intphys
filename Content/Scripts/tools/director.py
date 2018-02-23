import os

import unreal_engine as ue
from unreal_engine import FVector
from unreal_engine.classes import Screenshot

from tools.scene import TrainScene, TestScene
from tools.tick import Tick
from tools.utils import exit_ue
from actors.camera import Camera


class Director:
    """Render a list of intuitive physics scenes, optionally capture them

    The director renders each scene defined in the `scenes` list in
    the given UE `world`. It optionally takes screenshots and saves
    them to `output_dir`.

    The director is linked with the running game through the tick()
    method, in which it triggers the successive scenes.

    Parameters
    ----------
    world : ue.uobject
        The game's world in which to render the scenes
    scenes : list
        A list of scenes to render, can be either instance of the
        class TrainScene or TestScene
    size : tuple
        The size of a scene the screen resolution times the number of
        images captured in a single scene, in the form (width, height,
        nimages).
    output_dir : str, optional
        When specified, the directory where to write PNG images and
        metadata from the rendered scenes. When ignored (default), do
        not take captures nor save any data (dry mode).

    """
    def __init__(self, world, scenes, size, output_dir=None):
        self.world = world
        self.scenes_list = scenes
        self.size = size
        self.output_dir = output_dir

        ue.log('scheduling {nscenes} scenes, ({ntest} for test and '
               '{ntrain} for train), total of {nruns} runs'.format(
            nscenes=len(self.scenes_list),
            ntest=len([s for s in self.scenes_list if isinstance(s, TestScene)]),
            ntrain=len([s for s in self.scenes_list if isinstance(s, TrainScene)]),
            nruns=sum(s.get_nruns() for s in self.scenes_list)))

        # the director owns the camera
        self.camera = Camera(world, FVector(0, 0, 150))

        # initialize to render the first scene on the next tick
        self.scene_index = 0
        self.scene = self.scenes_list[0]
        self.setup()

        # start the ticker, take a screen capture each 2 game ticks
        self.ticker = Tick(tick_interval=2)
        self.ticker.is_ticking = True

    def tick(self, dt):
        """This method is called at each game tick"""
        tick = self.ticker.tick(dt)

        # we are not ticking, nothing to do
        if tick == -1:
            return

        # during a run, take screenshot
        elif tick < self.size[2]:
            self.capture()

        # end of a run, terminate it and setup the next one
        elif tick > self.size[2]:
            is_next_run = self.teardown()

            if is_next_run is True:
                self.ticker.counter = 0
                self.setup()

    def setup(self):
        description = 'running scene {}/{}: {}'.format(
            self.scene_index+1, len(self.scenes_list),
            self.scene.description())
        ue.log(description)

        # setup the screenshots
        if  self.scene.is_check_run():
            pass
        elif self.output_dir:
            Screenshot.Initialize(
                int(self.size[0]), int(self.size[1]), int(self.size[2]),
                self.camera.get_actor())

        # render the scene: spawn actors
        self.scene.render()

    def capture(self):
        if self.scene.is_check_run():
            # Screenshot.CaptureMasks()
            pass
        elif self.output_dir:
            Screenshot.Capture()

    def teardown(self):
        """Save captured images and prepare the next run

        Return True if there is a run to render, False otherwise.

        """
        if self.scene.is_check_run():
            return True
        else:
            # if the current run failed, restart the whole scene with new
            # random parameters
            if not self.scene.is_valid():
                ue.log('scene failed, retry it')
                self.scene.reset()
                return True

            # the run was successful, see if we need to save capture and
            # prepare the next run
            elif self.output_dir:
                self._save_capture()

            # prepare the next run : if no more run for that scene, render
            # the next scene (else render the next run of the current
            # scene: the runs transition is handled directly by the scene
            # instance)
            if self.scene.get_nruns_remaining() == 0:
                self.scene.clear()

                self.scene_index += 1
                try:
                    self.scene = self.scenes_list[self.scene_index]
                except IndexError:
                    ue.log_warning('all scenes rendered, exiting')

                    # stop the ticker while the program exits
                    self.ticker.is_ticking = False
                    exit_ue(self.world)
                    return False

            return True

    def _save_capture(self):
        # save the captured images in a subdirectory
        output_dir = self._get_scene_subdir()
        ue.log('saving screenshots to %s' % output_dir)

        done, max_depth, masks = Screenshot.Save(output_dir)

        if not done:
            self.ticker.is_ticking = False
            exit_ue(self.world, 'cannot save images to %s' % output_dir)

        return max_depth, masks


    def _get_scene_subdir(self):
        # build the scene sub-directory name, for exemple '027_test_O1'
        idx = self.scene_index + 1
        padded_idx = '0' * len(str(len(self.scenes_list) - idx)) + str(idx)
        scene_name = (
            padded_idx + '_' +
            ('train' if self.scene.is_train_scene() else 'test') + '_' +
            self.scene.scenario)

        out = os.path.join(self.output_dir, scene_name)

        if not self.scene.is_train_scene():
            # 1, 2, 3 and 4 subdirectories for test scenes
            run_idx = self.scene.get_nruns() - self.scene.current_run + 1
            out = os.path.join(out, str(run_idx))

        return out
