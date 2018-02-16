import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseMesh import BaseMesh
import tools.materials
import random
from actors.wall import Wall

"""
Walls is a wrapper class that make 3 walls spawn.
"""

class Walls():
    def __init__(self, world,
                 length = random.uniform(1500, 4000),
                 depth = random.uniform(1500, 900), # Why negative value ?
                 height = random.uniform(1, 10),
                 material = tools.materials.get_random_material(tools.materials.load_materials('Materials/Wall'))):
        self.front = Wall(world, "Front", length, depth, height, material)
        self.right = Wall(world, "Right", length, depth, height, material)
        self.left = Wall(world, "Left", length, depth, height, material)
