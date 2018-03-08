import unreal_engine as ue
from magical_value import MAGICAL_VALUE
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

from actors.base_mesh import BaseMesh
import tools.materials
import random
from collections import defaultdict
from actors.wall import Wall

"""
Walls is a wrapper class that make 3 walls spawn.
"""

class Walls():
    def __init__(self, world,
                 length = MAGICAL_VALUE,
                 depth = MAGICAL_VALUE,
                 height = MAGICAL_VALUE,
                 material = None,
                 manage_hits = True):
        self.get_parameters(length, depth, height, material, manage_hits)
        self.front = Wall(world, "Front",
                          self.length, self.depth,
                          self.height, self.material, self.manage_hits)
        self.right = Wall(world, "Right",
                          self.length, self.depth,
                          self.height, self.material, self.manage_hits)
        self.left = Wall(world, "Left",
                          self.length, self.depth,
                          self.height, self.material, self.manage_hits)

    def actor_destroy(self):
        self.front.actor_destroy()
        self.right.actor_destroy()
        self.left.actor_destroy()
        
    def get_parameters(self, length, depth, height, material, manage_hits):
        self.manage_hits = manage_hits
        if (depth == MAGICAL_VALUE):
            self.depth = random.uniform(900, 1500)
        else:
            self.depth = depth
        if (length == MAGICAL_VALUE):
            self.length = random.uniform(1500, 4000)
        else:
            self.length = length
        if (height == MAGICAL_VALUE):
            self.height = random.uniform(1, 10)
        else:
            self.height = height
        if (material == None):
            self.material = tools.materials.get_random_material(tools.materials.load_materials('Materials/Wall'))
        else:
            self.material = material

    def get_status(self):
        print(self.front.get_status())
        print(self.left.get_status())
        print(self.right.get_status())
        return None
