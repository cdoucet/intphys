import json
import os

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Screenshot

from tools.scene import Scene
from tools.tick import Tick
from tools.utils import exit_ue, set_game_paused

from actors.camera import Camera
from actors.parameters import CameraParams


class Director:
    """Render, capture and save a list of train and test scenes

    The 'movie director' renders each scene defined in the `scenes`
    list in the given UE `world`. It manages the transition between
    the different scenes and the different steps of a single scene:
    generating parameters, spawning the actors, rendering the
    different checks and runs, taking and saving screenshots. Those
    are triggered by the tick() method, which is automatically called
    by UE at each game's tick.

    Parameters
    ----------
    world : ue.uobject
        The game's world in which to render the scenes
    scenario_list : list
        A list of scenes to render, derived from scenario.base.Base
    size : tuple
        The size of a scene the screen resolution times the number of
        images captured in a single scene, in the form (width, height,
        nimages).
    output_dir : str, optional
        When specified, the directory where to write PNG images and
        metadata from the rendered scenes. When ignored (default), do
        not take captures nor save any data (dry mode).
    tick_interval: int, optional
        The tick interval (in number of game's ticks) between two
        captures. Default to 2.
    tick_pause_at_start: int, optional
        Pause the game at beginning of a run for `tick_pause_at_start`
        intervals. This allows the textures and materials to be completly
        loaded before the first capture. Default to 10 ticks.

    """
    def __init__(self, world, scenario_list, size, output_dir=None,
                 tick_interval=2, tick_pause_at_start=10):
        self.world = world
        self.scenario_list = scenario_list
        self.size = size
        self.output_dir = output_dir
        self.tick_pause_at_start = tick_pause_at_start

        ue.log('scheduling {nscenes} scenes, ({ntest} for test and '
               '{ntrain} for train), total of {nruns} runs'.format(
            nscenes=len(self.scenario_list),
            ntest=len([s for s in self.scenario_list if not s.is_train()]),
            ntrain=len([s for s in self.scenario_list if s.is_train()]),
            nruns=sum(s.get_nruns() for s in self.scenario_list)))

        # the director owns the camera (placed at (0, 0) by default,
        # two meters high)
        self.camera = Camera(world=world, params=CameraParams(
            location=FVector(0, 0, 200),
            rotation=FRotator(0, 0, 0)))

        # start the ticker, take a screen capture each 2 game ticks
        self.ticker = Tick(tick_interval=tick_interval)
        self.ticker.start()

        # an empty list to append status along the run
        self.status = []

        # initialize to render the first scene on the next tick
        self.scene_index = 0
        self.scene = Scene(world, self.scenario_list[0])
        self.setup()

    def tick(self, dt):
        """This method is called at each game tick by UE"""
        # update the ticker
        self.ticker.tick(dt)

        # # moving occluders and actors at every game tick
        # for actor in self.scene.get_moving_actors().values():
        #     actor.move()

        # if we are not ticking at low rate, nothing more to do
        if not self.ticker.on_tick():
            return

        # retrieve the number of ticks since the run's start
        tick = self.ticker.get_count()

        # manage the pause at beginning
        if tick <= self.tick_pause_at_start:
            return
        if tick == self.tick_pause_at_start + 1:
            set_game_paused(self.world, False)

        # during a run, take screenshot
        if tick <= self.size[2] + self.tick_pause_at_start:
            self.capture()

        # end of a run, terminate it
        if tick == self.size[2] + self.tick_pause_at_start:
            is_next_run = self.teardown()
            if is_next_run is True:
                self.setup()
            else:
                ue.log('all scenes rendered, exiting')
                self.ticker.stop()
                exit_ue(self.world)

    def setup(self):
        description = 'running scene {}/{}: {}'.format(
            self.scene_index+1, len(self.scenario_list),
            self.scene.description())
        ue.log(description)

        # setup the screenshots
        if self.scene.is_check_run():
            pass
        elif self.output_dir:
            Screenshot.Initialize(
                int(self.size[0]), int(self.size[1]), int(self.size[2]),
                self.camera.get_actor())

        # render the scene: spawn actors
        self.scene.render()
        self.ticker.reset()
        set_game_paused(self.world, True)

    def capture(self):
        if self.scene.is_check_run():
            # Screenshot.CaptureMasks()
            pass
        elif self.output_dir:
            Screenshot.Capture()
            self.status.append(self.scene.get_status())

    def teardown(self):
        """Save captured images for the current run and prepare the next one

        Return True if there is a next run to render, False otherwise.

        """
        # if the current run failed, restart the whole scene with new
        # random parameters
        if not self.scene.is_valid():
            ue.log('scene failed, retry it')
            self.scene.reset()
            return True

        # the run was successful, see if we need to save capture and
        # prepare the next run
        if self.output_dir and not self.scene.is_check_run():
            # save the captured images in a subdirectory
            output_dir = self.get_scene_subdir()
            ue.log('saving capture to %s' % output_dir)

            max_depth, masks = self.save_capture(output_dir)
            self.status['images'] = {'max_depth': max_depth, 'masks': masks}

            self.save_status(os.path.join(output_dir, 'status.json'))

        # prepare the next run : if no more run for that scene, render
        # the next scene. Else render the next run of the current
        # scene: the runs transition is handled directly by the scene
        # instance.
        if self.scene.get_nruns_remaining() > 0:
            return True
        else:
            # destroy all the actors from the previous scene
            self.scene.clear()
            self.scene_index += 1
            try:
                scenario = self.scenario_list[self.scene_index]
                self.scene = Scene(self.world, scenario)
                return True
            except IndexError:
                return False

    def save_capture(self, output_dir):
        done, max_depth, masks = Screenshot.Save(output_dir)
        if not done:
            self.ticker.stop()
            exit_ue(self.world, 'cannot save images to %s' % output_dir)
        return max_depth, masks

    def save_status(self, json_file):
        open(json_file, 'w').write(json.dumps(self.status, indent=4))

    def get_scene_subdir(self):
        # build the scene sub-directory name, for exemple
        # '027_test_O1/3' or '028_train_O1'
        idx = self.scene_index + 1
        padded_idx = '0' * len(str(len(self.scenario_list) - idx)) + str(idx)
        scene_name = (
            padded_idx + '_' +
            ('train' if self.scene.is_train_scene() else 'test') + '_' +
            self.scene.scenario.name)

        out = os.path.join(self.output_dir, scene_name)

        if not self.scene.is_train_scene():
            # 1, 2, 3 and 4 subdirectories for test scenes
            run_idx = self.scene.get_nruns() - self.scene.current_run + 1
            out = os.path.join(out, str(run_idx))

        return out
