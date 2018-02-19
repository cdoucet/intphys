import os

import unreal_engine as ue


class ScenesJsonParser:
    @staticmethod
    def parse(scenes_json):
        scenes = []
        # iterate on the blocks defined in the configuration
        for scenario, cases in scenes_json.items():
            # 'scenario_O1' -> 'O1'
            scenario = scenario.split('_')[1]

            for k, v in cases.items():
                if 'train' in k:
                    nscenes = v
                    scenes += [TrainScene(scenario)] * nscenes
                else:  # test scenes
                    is_occluded = 'occluded' in k
                    for condition, nscenes in v.items():
                        is_static = 'static' in condition
                        ntricks = 2 if condition.endswith('2') else 1

                        scenes += [TestScenes(scenario, is_occluded, is_static, ntricks)] * nscenes

        return scenes


class Scheduler:
    def __init__(self, scenes_json, output_dir):
        scenes_list = ScenesJsonParser.parse(scenes_json)

        ue.log('scheduling {nscenes} scenes, ({ntest} for test and '
               '{ntrain} for train), total of {nruns} runs'.format(
            nscenes=len(scenes_list),
            ntest=len([s for s in scenes_list if isinstance(s, TestScene)]),
            ntrain=len([s for s in scenes_list if isinstance(s, TrainScene)]),
            nruns=sum(s.get_nruns() for s in scenes_list)))

    def run(self):
        pass

    def tick(self):
        pass
