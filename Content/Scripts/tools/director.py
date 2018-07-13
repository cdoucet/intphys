import json
import importlib
import time
import unreal_engine as ue
import tools.materials
from tools.utils import exit_ue, set_game_paused
from tools.saver import Saver


class Director(object):
    def __init__(self, world, params_file, size, output_dir, tick_interval=2):
        self.world = world
        self.scenes = []
        self.scene = 0
        self.saver = Saver(
                size=size,
                dry_mode=True if output_dir is None else False,
                output_dir=output_dir)
        try:
            self.scenarios_dict = json.loads(open(params_file, 'r').read())
            self.generate_scenes(params_file)
        except ValueError as e:
            print(e)
        except BufferError as e:
            print(e)
        # start the ticker, take a screen capture each 2 game ticks
        # self.ticker = Tick(tick_interval=tick_interval)
        # self.ticker.start()
        self.ticker = 0
        self.pause = False
        self.was_paused = False
        tools.materials.load()
        self.restarted = 0

    def generate_scenes(self, params_file):
        for scenario, a in self.scenarios_dict.items():
            # 'scenario_O1 -> 'O1'
            scenario = scenario.split('_')[1]
            # import the class of the corresponding scenario
            module = importlib.import_module("scenario.{}".format(scenario))
            train_class = getattr(module, "{}Train".format(scenario))
            test_class = getattr(module, "{}Test".format(scenario))
            for scene, b in a.items():
                if ('train' in scene):
                    for i in range(b):
                        self.scenes.append(train_class(self.world, self.saver))
                elif ('test' in scene):
                    if ('occluded' in scene):
                        is_occluded = True
                    elif ('visible' in scene):
                        is_occluded = False
                    else:
                        raise BufferError("Didn't find 'occluded' nor 'visi" +
                                          "ble' in one scene of the json file")
                    for movement, nb in b.items():
                        if ('static' not in movement and
                                'dynamic_1' not in movement and
                                'dynamic_2' not in movement):
                            raise BufferError("Didn't find 'static', " +
                                              "'dynamic_1' nor 'dynamic_2' " +
                                              "in one scene of the json file")
                        else:
                            for i in range(nb):
                                self.scenes.append(test_class(self.world,
                                                              self.saver,
                                                              is_occluded,
                                                              movement))
                else:
                    raise BufferError("Didn't find 'train' nor 'test' in one" +
                                      "scenario of the json file")

    def play_scene(self):
        if self.scene >= len(self.scenes):
            return
        if self.scenes[self.scene].run == 0:
            if hasattr(self.scenes[self.scene], 'movement'):
                ue.log("Scene {}/{}: Test / scenario {} / {} / {}".format(
                    self.scene + 1, len(self.scenes),
                    self.scenes[self.scene].name,
                    self.scenes[self.scene].movement,
                    "occluded" if self.scenes[self.scene].is_occluded
                    is True else "visible"))
            else:
                ue.log("Scene {}/{}: Train / scenario {}".format(
                    self.scene + 1, len(self.scenes),
                    self.scenes[self.scene].name))
        self.scenes[self.scene].play_run()

    def stop_scene(self):
        if self.scene >= len(self.scenes):
            return
        if self.scenes[self.scene].stop_run(self.scene,
                                            len(self.scenes)) is False:
            self.restart_scene()
        elif (self.scenes[self.scene].is_over() and
                self.scene < len(self.scenes)):
            self.scene += 1
        self.ticker = 0

    def restart_scene(self):
        ue.log('Restarting scene')
        self.restarted += 1
        self.saver.reset(True)
        is_test = True if 'test' in \
            type(self.scenes[self.scene]).__name__.lower() else False
        module = importlib.import_module("scenario.{}".
                                         format(self.scenes[self.scene].name))
        if is_test is True:
            test_class = getattr(module,
                                 "{}Test".format(self.scenes[self.scene].name))
            is_occluded = self.scenes[self.scene].is_occluded
            movement = self.scenes[self.scene].movement
            self.scenes.insert(self.scene + 1, test_class(self.world,
                                                          self.saver,
                                                          is_occluded,
                                                          movement))
            self.scenes.pop(0)
        else:
            train_class = \
                getattr(module, "{}Train".format(self.scenes[self.scene].name))
            self.scenes.insert(self.scene + 1,
                               train_class(self.world, self.saver))
            self.scenes.pop(0)

    def capture(self):
        self.scenes[self.scene].capture()

    def tick(self, dt):
        """ this method is called at each game tick by UE """
        if self.pause is True:
            # TODO
            time.sleep(2)
            self.pause = False
            return

        # launch new scene every 200 tick except if a pause just finished
        if self.was_paused is False and self.ticker % 200 == 0:
            if self.ticker != 0:
                self.stop_scene()
            self.play_scene()
            # pause to let textures load
            self.pause = True
            self.was_paused = True
            set_game_paused(self.world, True)
            return

        # if one of the actors is not valid, restart the scene with
        # new parameters, in a try/catch to deals with the very last
        # scene once it have been stopped
        try:
            if not self.scenes[self.scene].is_valid():
                self.scenes[self.scene].stop_run(self.scene, len(self.scenes))
                self.restart_scene()
                self.ticker = 0
                self.play_scene()
                # pause to let textures load
                self.pause = True
                self.was_paused = True
                set_game_paused(self.world, True)
                return
        except IndexError:
            pass

        self.was_paused = False
        set_game_paused(self.world, False)
        if self.scene < len(self.scenes):
            self.scenes[self.scene].tick()
            if self.ticker % 2 == 1:
                self.capture()
        else:
            ue.log("Restarted {} scenes.".format(self.restarted))
            exit_ue("The end")
        self.ticker += 1
