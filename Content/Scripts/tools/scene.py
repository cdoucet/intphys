import unreal_engine as ue
from unreal_engine import FVector, FRotator

from unreal_engine.enums import ECameraProjectionMode
from actors.floor import Floor
from actors.object import Object
from actors.occluder import Occluder
from actors.walls import Walls
from actors.camera import Camera
from actors.light import Light
import json
from tools.materials import get_random_material
from tools.materials import load_materials
import random

class BaseScene:
    def __init__(self, world, scenario):
        self.world = world
        self.scenario = scenario
        self.current_run = 0
        self.actors = { "Camera": None, "Floor": None, "Light": None, "Walls": None, "Occluder": [], "Object": [] }

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

    def print_status(self):
        for key, value in self.actors.items():
            if (isinstance(value, list)):
                for member in value:
                    print(member.get_status())
            else:
                if (value != None):
                    print(value.get_status())
                    

    def render(self):
        """
        # # TODO generate parameters and spawn the actors
        self.actors["Camera"] = Camera(
                                       world = self.world,
                                       location = FVector(-500, 0, 150),
                                       rotation = FRotator(0, 0, 0))
        self.actors["Floor"] = Floor(world = self.world,
                                     friction = 1)
        self.actors["Light"] = Light(world = self.world,
                                     type = 'SkyLight',
                                     location = FVector(-1000, 0, 1000),
                                     rotation = FRotator(0, -45, 0))
        moves_array = []
        moves_array.append(100)
        moves_array.append(0)
        self.actors["Occluder"].append(Occluder(world = self.world,
                                                material = get_random_material(load_materials('Materials/Actor')),
                                                rotation = FRotator(0, 0, 90),
                                                location = FVector(0, 0, 150),
                                                speed = 1,
                                                moves = moves_array))
        """
        self.spawn_actors()
        self.print_status()
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
            
    def spawn_actors(self):
        self.actors["Camera"] = Camera(world = self.world,
                                       location = FVector(-1000, 0, 5000),
                                       rotation = FRotator(0, -90, 0),
                                       field_of_view = 90,
                                       aspect_ratio = 1,
                                       projection_mode = ECameraProjectionMode.Perspective,
                                       manage_hits = True)
        self.actors["Floor"] = Floor(world = self.world,
                                     material = get_random_material(load_materials('Materials/Floor')),
                                     scale = FVector(100, 100, 1),
                                     friction = random.uniform(-1000, 1000))
        self.actors["Light"] = Light(world = self.world,
                                     type = 'SkyLight',
                                     location = FVector(0, 0, 1000),
                                     rotation = FRotator(0, 0, 0),
                                     manage_hits = True)
        if (random.randint(0, 1) == 1):
            self.actors["Walls"] = Walls(world = self.world,
                                         height = random.uniform(1, 10),
                                         length = random.uniform(1500, 4000),
                                         depth = random.uniform(900, 1500),
                                         material = get_random_material(load_materials('Materials/Wall')),
                                         manage_hits = True)
        else:
            self.actors["Walls"] = None
        for i in range(1, random.randint(1, 3)):
            scale_value = random.uniform(0.5, 1)
            self.actors["Object"].append(Object(world = self.world,
                                                mesh_str = Object.shape['Sphere'],
                                                location = FVector(random.uniform(-500, 500),
                                                                   random.uniform(-500, 500),
                                                                   random.uniform(0, 100) + (50 * scale_value)),
                                                rotation = FRotator(random.uniform(-180, 180),
                                                                    random.uniform(-180, 180),
                                                                    random.uniform(-180, 180)),
                                                scale = FVector(scale_value,
                                                                scale_value,
                                                                scale_value),
                                                material = get_random_material(load_materials('Materials/Actor')),
                                                mass = random.uniform(1, 500),
                                                force = FVector(random.uniform(-1e8, 1e8),
                                                                random.uniform(-1e8, 1e8),
                                                                0),
                                                friction = random.uniform(-1000, 1000),
                                                manage_hits = True))
        for i in range(1, random.randint(1, 3)):
            moves_array = []
            for j in range(1, random.randint(0, 2)):
                moves_array.append(random.randint(1, 200))
            self.actors["Occluder"].append(Occluder(world = self.world,
                                                    location = FVector(random.uniform(-500, 500),
                                                                       random.uniform(-500, 500),
                                                                       random.uniform(-500, 500)),
                                                    rotation = FRotator(0,
                                                                        0,
                                                                        random.uniform(-180, 180)),
                                                    scale = FVector(random.uniform(1, 10),
                                                                    1,
                                                                    random.uniform(1, 10)),
                                                    material = get_random_material(load_materials('Materials/Wall')),
                                                    speed = random.uniform(0.5, 10),
                                                    moves = moves_array))
        
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
