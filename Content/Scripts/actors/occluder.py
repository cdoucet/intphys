# coding: utf-8

import unreal_engine as ue
from unreal_engine.classes import Material
from unreal_engine import FVector
from actors.base_mesh import BaseMesh
from actors.parameters import OccluderParams


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


Occluder is the vertical plane thing that sometimes fall and sometimes get up by itself.
Sounds weird, it is.
It inherits from BaseMesh.
The occluder spawns verticaly.

ABOUT the moves variable : it is an array which shall contain the frames when
you want the occluder to initiate a movement (it moves at 1 degree per frame).
ergo, if you want the occluder to move at the first frame, put 0 in the array.
The occluder will come down. If you put 50, it won't have time to fully go
down : it will rise again at the 50th frame
"""


class Occluder(BaseMesh):
    def __init__(self, world, params=OccluderParams()):
        super().__init__(
            world.actor_spawn(ue.load_class('/Game/Occluder.Occluder_C')))
        self.get_parameters(params)
        self.set_parameters()

    def get_parameters(self, params):
        # TODO this thing is a non-sense (we apply to the y location
        # the x scale...)  maybe it's time to drop out the
        # normalization
        location = FVector(
                params.location.x,
                params.location.y,
                params.location.z)
        location.y = location.y - (params.scale.x * 200)
        super().get_parameters(
            location,
            params.rotation,
            params.scale,
            params.friction,
            params.restitution,
            params.overlap,
            params.warning,
            '/Game/Meshes/OccluderWall')
        self.material = ue.load_object(Material, params.material)
        self.speed = params.speed
        # array of numbers from 1 to 200
        self.moves = params.moves
        self.moving = False
        self.up = params.start_up
        if (self.up is False):
            self.rotation.roll = 90
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
            if (self.moving is False):
                if (self.up is True):
                    rotation.roll += self.speed
                else:
                    rotation.roll -= self.speed
                self.moving = True
            else:
                if (self.up is True):
                    rotation.roll += self.speed
                    self.up = False
                else:
                    rotation.roll -= self.speed
                    self.up = True
        elif (self.moving is True):
            if (self.up is True):
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
        status['moves'] = []
        for i in self.moves:
            status['moves'].append(i)
        return status

    def on_actor_overlap(self, me, other):
        super().on_actor_overlap(me, other)
        if 'occluder' in other.get_name().lower():
            self.is_valid = False

    def on_actor_hit(self, me, other, *args):
        super().on_actor_hit(me, other)
        if 'occluder' in other.get_name().lower():
            self.is_valid = False

    def reset(self, params):
        super().reset(params)
        self.set_location(FVector(self.location.x, self.location.y - (self.scale.x * 200), self.location.z))
        self.moving = False
        self.count = -1
        self.up = params.start_up
        if (self.up is False):
            self.rotation.roll = 90
