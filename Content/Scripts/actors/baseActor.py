import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel

"""
BaseActor is the very base of the inheritance tree.
It is the base class of every python component build with an actor (all of them, though).
Beware : this is a recursive instantiation (see comments at the begining of other classes)
Therefore, don't try to use the self.actor before the actor_spawn function is called
"""

class BaseActor():
    """
    __init__ instantiate the class
    parameters ->
    actor: spawned actor (UObject)
    location: location of the actor (FVector). Default value: 0, 0, 0
    rotation: rotation of the actor (FRotator). Default value: 0, 0, 0
    """
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
        if (self.actor.set_actor_location(self.location, False) == False):
            print("Failed to set the location of an actor")
        
    def set_rotation(self, rotation):
        self.rotation = rotation
        if (self.actor.set_actor_rotation(self.rotation, True) == False):
            print("Failed to set the rotation of an actor")

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps this object"""
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log_error(message)
