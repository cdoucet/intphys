# coding: utf-8

import unreal_engine as ue
from magical_value import MAGICAL_VALUE
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

from actors.base_mesh import BaseMesh
import tools.materials
import random

"""
Ok here we go:
This is a recursive instantiate class.
The general principle is to instantiate a class twice to avoid making two distinct classes.
I needed to instantiate a python component with parameters but UnrealEnginePython
wouldn't let me do that.
Furthermore, I couldn't spawn the actor without instanciate the class and thus,
I couldn't spawn it with any parameter.

Let me explain myself :
In the main, I call the constructor of the class Object (for instance, or Floor, or Occluder),
which call the __init__ function of Object with at least 1 argument, world
which call the __init__function of BaseMesh with at least 1 argument, mesh_str.
In the Object __init__ function, I call actor_spawn,
which implicitely instanciate Object (yes, again)
BUT during the second instantiation, no parameters is given to __init__ (of Object and BaseMesh)
(this is why there is default values to every parameters of __init__).
Thus, if __init__ is called without any parameters, I know that it is the second instantiation,
so I don't spawn the actor again.
Once the object spawned, all I have to do is to set the parameters in the second instantiation
(location, rotation,...).
Et voilà !
"""

"""
Occluder is the vertical plane thing that sometimes fall and sometimes get up by itself.
Sounds weird, it is.
It inherits from BaseMesh.
"""

class Occluder(BaseMesh):
    """
    __init__ instantiate the class
    parameters ->
    world: UEngine world instance
    mesh_str: the path of the mesh/shape of the actor (str). Default value: a sphere
    location: location of the actor (FVector). Default value: 0, 0, 0
    rotation: rotation of the actor (FRotator). Default value: 0, 0, 0
    scale: scale of the actor (FVector). Default value: 1, 1, 1
    material: material of the actor (str). Default value: a random one in the relevant directory

    Warning !
    The location is precisely from the point at the bottom center of the mesh
    """
    def __init__(self,
                 world = None,
                 location = FVector(0, 0, 0),
                 rotation = FRotator(0, 0, 0),
                 scale = FVector(1, 1, 1),
                 material = None,
                 moves = [0],
                 speed = 1,
                 manage_hits = True):
        if (world != None):
            super().__init__(world.actor_spawn(ue.load_class('/Game/Occluder.Occluder_C')))
            self.get_parameters(location, rotation,
                                scale, material,
                                moves, speed,
                                manage_hits)
            self.set_parameters()
        else:
            super().__init__()

    def get_parameters(self, location, rotation,
                       scale, material, moves,
                       speed, manage_hits):
        super().get_parameters(location, rotation, scale,
                               0.5, manage_hits,
                               '/Game/Meshes/OccluderWall')
        self.material = ue.load_object(Material, material)
        self.speed = speed
        self.moves = moves
        self.moving = False
        self.up = True
        self.location.y - (200 * scale.y)
        self.count = -1

    def set_parameters(self):
        super().set_parameters()
        
        
    """
    make the Occluder fall and get up when called
    """
    def move(self):
        self.count += 1
        rotation = self.rotation
        if (self.count in self.moves):
            if (self.moving == False):
                if (self.up == True):
                    rotation.roll += self.speed
                else:
                    rotation.roll -= self.speed
                self.moving = True
            else:
                if (self.up == True):
                    rotation.roll += self.speed
                    self.up = False
                else:
                    rotation.roll -= self.speed
                    self.up = True
        elif (self.moving == True):
            if (self.up == True):
                rotation.roll += self.speed
            else:
                rotation.roll -= self.speed
        else:
            return
        if (rotation.roll >= 90):
            rotation.roll = 90
            self.up = False
            self.moving = False
        elif (rotation.roll <= 0):
            rotation.roll = 0
            self.up = True
            self.moving = False
        self.set_rotation(rotation)

    def get_status(self):
        status = super().get_status()
        status['material'] = self.material.get_name()
        status['speed'] = self.speed
        for i in self.moves:
            status['moves'].append(i)
        return status
