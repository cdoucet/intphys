import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

class BaseActor():
    def __init__(self, location, rotation):
        self.location = location
        self.rotation = rotation

    def get_status():
        return self.location, self.rotation

    def set_location(x, y = None, z = None):
        if (y == None and z == None):
            self.location = x
        else:
            self.location = FVector(x, y, z)
        actor.set_actor_location(self.location)
        
    def set_rotation(x, y = None, z = None):
        if (y == None and z == None):
            self.rotation = x
        else:
            self.rotation = FRotator(x, y, z)
        actor.set_actor_rotation(self.rotation)
