import unreal_engine as ue
from unreal_engine import FVector, FRotator

import tools.materials

from actors.floor import Floor
from actors.object import Object
from actors.occluder import Occluder
from actors.walls import Walls
from actors.camera import Camera

import json

class BaseScene:
    def __init__(self, world, scenario):
        self.world = world
        self.scenario = scenario
        self.current_run = 0
        self.actors = { "Camera": None, "Floor": None, "Walls": None, "Occluder": [], "Object": [] }

    def get_nruns(self):
        return 1

    def get_nruns_remaining(self):
        return self.get_nruns() - self.current_run

    def is_valid(self):
        return True

    def is_train_scene(self):
        return True if isinstance(self, TrainScene) else False

    def is_check_run(self):
        return False

    def description(self):
        """Return a string description of the scene's current run"""
        raise NotImplementedError

    def render(self):
        # # TODO generate parameters and spawn the actors
        self.actors["Camera"] = Camera(world = self.world, location = FVector(-500, 0, 150), rotation = FRotator(0, 0, 0))
        self.actors["Floor"] = Floor(world = self.world,
                                     friction = 1)
        """
        self.actors["Walls"] = Walls(self.world)
        self.actors["Occluder"].append(Occluder(world = self.world,
                                                rotation = FRotator(0, 0, 90),
                                                speed = 5,
                                                moves = 3,
                                                pause = True))
        """
        self.actors["Object"].append(Object(world = self.world,
                                            mesh_str = Object.shape['Sphere'],
                                            location = FVector(200, -500, 100),
                                            force = FVector(0, 1e8, 0),
                                            manage_hits = True,
                                            friction = 1))
        self.actors["Object"].append(Object(world = self.world,
                                            mesh_str = Object.shape['Sphere'],
                                            location = FVector(200, 500, 100),
                                            force = FVector(0, -1e8, 0),
                                            manage_hits = True,
                                            friction = 1))
        print(json.dumps(self.actors["Object"][0].get_status(), indent = 4))
        print(json.dumps(self.actors["Object"][1].get_status(), indent = 4))
        # prepare for the next run
        self.current_run += 1

    def clear(self):
        for key, value in self.actors.items():
            if (isinstance(value, list)):
                for member in value:
                    member.actor_destroy()
                value[:] = []
            else:
                if (value != None):
                    value.actor_destroy()
                value = None
            
                
class TrainScene(BaseScene):
    def __init__(self, world, scenario):
        super(TrainScene, self).__init__(world, scenario)

    def description(self):
        return self.scenario + ' train'


class TestScene(BaseScene):
    def __init__(
            self, world, scenario,
            is_occluded=False, is_static=False, ntricks=1):
        super(TestScene, self).__init__(world, scenario)

        self.is_occluded = is_occluded
        self.is_static = is_static
        self.ntricks = ntricks

    def description(self):
        return (
            self.scenario + ' test' +
            (' occluded' if self.is_occluded else ' visible') +
            (' static' if self.is_static else ' dynamic_{}'.format(self.ntricks)) +
            ' ({}/{})'.format(self.current_run+1, self.get_nruns()))

    def is_check_run(self):
        return self.current_run < self.get_nruns_check()

    def get_nruns(self):
        return 4 + self.get_nruns_check()

    def get_nruns_check(self):
        # TODO should be retrieved for scenario class
        nruns = 0
        if not self.is_occluded:
            nruns = 0
        elif self.ntricks == 2:
            nruns = 2
        else: # occluded single trick
            nruns = 1

        # block O2 has twice the checks of block O1
        if 'O2' in self.scenario:
            nruns *= 2

        return nruns
