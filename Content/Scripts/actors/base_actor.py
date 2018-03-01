import unreal_engine as ue
import random
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
    def __init__(self, actor = None, location = FVector(0, 0, -42), rotation = FRotator(0, 0, -42)):
        self.actor = actor
        self.location = location
        self.rotation = rotation
        self.hidden = False
        
    def actor_destroy(self):
        if (self.actor != None):
            self.actor.actor_destroy()
            self.actor = None
        self.actor = None

    def get_location(self):
        return self.location

    def get_rotation(self):
        return self.rotation

    def get_actor(self):
        return self.actor

    def set_actor(self, actor):
        self.actor = actor

    def set_location(self, location):
        self.location = location
        if (self.actor.set_actor_location(self.location, False) == False):
            ue.log_warning("Failed to set the location of an actor")

    def set_rotation(self, rotation):
        self.rotation = rotation
        if (self.actor.set_actor_rotation(self.rotation) == False):
            ue.log_warning("Failed to set the rotation of an actor")

    """Raises a Runtime error when some actor overlaps this object"""
    def manage_overlap(self, me, other):
        if (me == other):
            return
        message = '{} overlapping {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log_error(message)

    def on_actor_hit(self, me, other, *args):
        if (other.get_name()[:5] == "Floor"):
            return
        message = '{} hitting {}'.format(
            self.actor.get_name(), other.get_name())
        ue.log_error(message)

    """
    Returns random coordinates for train scenes
    In train scenes, camera has a high variability. Only the roll
    is forced to 0.
    """
    def get_train_parameters(self):
        location = FVector(
            random.uniform(-100, 100),
            random.uniform(200, 400),
            100 + random.uniform(-30, 80))
        rotation = FRotator(
            0,
            random.uniform(-15, 10),
            random.uniform(-30, 30))
        return location, rotation

    """
    Returns random coordinates for test scenes
    In test scenes, the camera has a constrained location, with
    little variations along the y axis and pitch.
    """
    def get_test_parameters(self):
        location = FVector(
            0,
            -100 * random.random(),
            150)
        rotation = FRotator(
            0,
            -10 * random.random(),
            0)
        return location, rotation

    def set_hidden(self, hidden):
        self.hidden = hidden
        self.actor.SetActorHiddenInGame(hidden)
