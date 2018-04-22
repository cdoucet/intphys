import json
import importlib
import unreal_engine as ue
from tools.tick import Tick
from tools.utils import exit_ue
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
        self.ticker = Tick(tick_interval=tick_interval)
        self.ticker.start()

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
                        raise BufferError("Didn't find 'occluded' nor 'visible' in one scene of the json file")
                    for movement, nb in b.items():
                        if ('static' not in movement and 'dynamic_1' not in movement and 'dynamic_2' not in movement):
                            raise BufferError("Didn't find 'static', 'dynamic_1' nor 'dynamic_2' in one scene of the json file")
                        else:
                            for i in range(nb):
                                self.scenes.append(test_class(self.world, self.saver, is_occluded, movement))
                else:
                    raise BufferError("Didn't find 'train' nor 'test' in one scenario of the json file")

    def play_scene(self):
        if self.scene >= len(self.scenes):
            return
        ue.log("Scene {}/{}:".format(self.scene + 1, len(self.scenes)))
        self.scenes[self.scene].play_run()

    def stop_scene(self):
        if self.scene >= len(self.scenes):
            return
        self.scenes[self.scene].stop_run()
        if self.scenes[self.scene].is_over() and self.scene < len(self.scenes):
            self.scene += 1

    def tick(self, dt):
        """ this method is called at each game tick by UE """
        # update the ticker
        self.ticker.tick(dt)
        if self.ticker.on_tick() is False:
            return
        if (self.ticker.get_count() - 1) % 100 == 0:
            if self.ticker.get_count() - 1 != 0:
                self.stop_scene()
            self.play_scene()
        if (self.scene < len(self.scenes)):
            self.scenes[self.scene].tick(self.ticker.get_count())
        else:
            exit_ue("the end")
            self.ticker.stop()
