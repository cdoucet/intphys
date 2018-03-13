import random

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.enums import ECameraProjectionMode

from actors.floor import Floor
from actors.object import Object
from actors.occluder import Occluder
from actors.walls import Walls
from actors.camera import Camera
from actors.light import Light
from tools.materials import get_random_material
from tools.materials import load_materials


class BaseScene:
    def __init__(self, world, scenario):
        self.world = world
        self.scenario = scenario
        self.current_run = 0

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
                if (value is not None):
                    print(value.get_status())

    def render(self):
        self.spawn_actors()
        # self.print_status()

        # prepare for the next run
        self.current_run += 1

    def clear(self):
        for key, value in self.actors.items():
            if (isinstance(value, list)):
                for member in value:
                    member.actor_destroy()
                value[:] = []
            else:
                if (value is not None):
                    value.actor_destroy()
                value = None


class TrainScene(BaseScene):
    def __init__(self, world, scenario):
        super(TrainScene, self).__init__(world, scenario)

    def description(self):
        return self.scenario + ' train'

    def spawn_actors(self):
        self.actors["Camera"] = Camera(
            world=self.world,
            location=FVector(-1000, 0, 200),
            rotation=FRotator(0, 0, 0),
            field_of_view=90,
            aspect_ratio=1,
            projection_mode=ECameraProjectionMode.Perspective,
            overlap=True,
            warning=True)

        self.actors["Floor"] = Floor(
            world=self.world,
            material=get_random_material(load_materials('Materials/Floor')),
            scale=FVector(100, 100, 1),
            friction=random.uniform(-1000, 1000))

        self.actors["Light"] = Light(
            world=self.world,
            type='SkyLight',
            location=FVector(0, 0, 1000),
            rotation=FRotator(0, 0, 0),
            overlap=True,
            warning=True)

        if random.randint(0, 1) == 1:
            self.actors["Walls"] = Walls(
                world=self.world,
                height=random.uniform(1, 10),
                length=random.uniform(1500, 4000),
                depth=random.uniform(900, 1500),
                material=get_random_material(load_materials('Materials/Wall')),
                overlap=False,
                warning=False)
        else:
            self.actors["Walls"] = None

        for i in range(1, random.randint(1, 3)):
            scale_value = random.uniform(0.5, 1)
            self.actors["Object"].append(
                Object(world=self.world,
                       mesh_str=Object.shape['Sphere'],
                       location=FVector(random.uniform(-500, 500),
                                        random.uniform(-500, 500),
                                        random.uniform(0, 100) + (50 * scale_value)),
                       rotation=FRotator(random.uniform(-180, 180),
                                         random.uniform(-180, 180),
                                         random.uniform(-180, 180)),
                       scale=FVector(scale_value,
                                     scale_value,
                                     scale_value),
                       material=get_random_material(load_materials('Materials/Actor')),
                       mass=random.uniform(1, 500),
                       force=FVector(random.uniform(-1e8, 1e8),
                                     random.uniform(-1e8, 1e8),
                                     0),
                       friction=random.uniform(-1000, 1000),
                       overlap=False,
                       warning=False))

        for i in range(1, random.randint(1, 3)):
            moves_array = []
            for j in range(1, random.randint(0, 2)):
                moves_array.append(random.randint(1, 200))
            self.actors["Occluder"].append(
                Occluder(
                    world=self.world,
                    location=FVector(random.uniform(-500, 500),
                                     random.uniform(-500, 500),
                                     0),
                    rotation=FRotator(0,
                                      0,
                                      random.uniform(-180, 180)),
                    scale=FVector(random.uniform(1, 2),
                                  1,
                                  random.uniform(1, 2)),
                    material=get_random_material(load_materials('Materials/Wall')),
                    speed=random.uniform(0.5, 10),
                    moves=moves_array,
                    overlap=False,
                    warning=False))


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
            self.scenario.get_description +
            ' ({}/{})'.format(self.current_run+1, self.get_nruns()))

    def is_check_run(self):
        return self.current_run < self.scenario.get_nruns_check()

    def get_nruns(self):
        return 4 + self.scenario.get_nruns_check()

    def spawn_actors(self):
        self.actors["Camera"] = Camera(
            world=self.world,
            location=FVector(0, -100 * random.random(), 150 + random.random()),
            rotation=FRotator(10 * random.random(), 10 * random.random(), 0),
            field_of_view=90,
            aspect_ratio=1,
            projection_mode=ECameraProjectionMode.Perspective,
            overlap=True,
            warning=True)

        self.actors["Floor"] = Floor(
            world=self.world,
            material=get_random_material(load_materials('Materials/Floor')),
            scale=FVector(100, 100, 1),
            friction=0.7)

        self.actors["Light"] = Light(
            world=self.world,
            type='SkyLight',
            location=FVector(0, 0, 1000),
            rotation=FRotator(0, 0, 0),
            overlap=True,
            warning=True)

        if (random.randint(0, 1) == 1):
            self.actors["Walls"] = Walls(
                world=self.world,
                height=random.uniform(1, 10),
                length=random.uniform(1500, 4000),
                depth=random.uniform(900, 1500),
                material=get_random_material(load_materials('Materials/Wall')),
                overlap=False,
                warning=True)
        else:
            self.actors["Walls"] = None
        object_number = random.randint(1, 3)
        for i in range(1, object_number):
            scale_value = random.uniform(0.5, 1)
            self.actors["Object"].append(
                Object(
                    world=self.world,
                    mesh_str=Object.shape['Sphere'],
                    location=FVector(random.uniform(-500, 500),
                                     random.uniform(-500, 500),
                                     random.uniform(0, 100) + (50 * scale_value)),
                    rotation=FRotator(random.uniform(-180, 180),
                                      random.uniform(-180, 180),
                                      random.uniform(-180, 180)),
                    scale=FVector(scale_value,
                                  scale_value,
                                  scale_value),
                    material=get_random_material(load_materials('Materials/Actor')),
                    mass=random.uniform(1, 500),
                    force=FVector(random.uniform(-1e8, 1e8),
                                  random.uniform(-1e8, 1e8),
                                  0),
                    friction=random.uniform(-1000, 1000),
                    overlap=False,
                    warning=True))

        for i in range(1, random.randint(1, 3)):
            moves_array = []
            for j in range(1, random.randint(0, 2)):
                moves_array.append(random.randint(1, 200))
            self.actors["Occluder"].append(
                Occluder(world=self.world,
                         location=FVector(random.uniform(-500, 500),
                                          random.uniform(-500, 500),
                                          0),
                         rotation=FRotator(0,
                                           0,
                                           random.uniform(-180, 180)),
                         scale=FVector(random.uniform(1, 10),
                                       1,
                                       random.uniform(1, 10)),
                         material=get_random_material(load_materials('Materials/Wall')),
                         speed=random.uniform(-1.5, 10),
                         moves=moves_array,
                         overlap=False,
                         warning=True))
