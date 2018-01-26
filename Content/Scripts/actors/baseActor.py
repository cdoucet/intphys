import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

class BaseActor():
    def __init__(self, actor = None, location = FVector(0, 0, 0), rotation = FRotator(0, 0, 0)):
        self.actor = actor
        self.location = location
        self.rotation = rotation

    def get_status(self):
        return self.location, self.rotation

    def get_actor(self):
        return self.actor

    def set_actor(self, actor):
        self.actor = actor

    def set_location(self, location):
        self.location = location
        self.actor.set_actor_location(self.location.x, self.location.y, self.location.z)

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.actor.set_actor_rotation(self.rotation.pitch, self.rotation.roll, self.rotation.yaw)

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps this object"""
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log_error(message)
