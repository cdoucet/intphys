import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

class BaseActor():
    def __init__(self, location, rotation):
        self.location = location
        self.rotation = rotation

    def get_status(self):
        return self.location, self.rotation

    def set_location(self, location):
        self.location = location
        self.actor.set_actor_location(self.location)

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.actor.set_actor_rotation(self.rotation)
