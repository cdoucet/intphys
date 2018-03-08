import unreal_engine as ue
import random
from magical_value import MAGICAL_VALUE
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from collections import defaultdict

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
    def __init__(self, actor = None):
        self.actor = actor

    def actor_destroy(self):
        if (self.actor != None):
            self.actor.actor_destroy()
            self.actor = None
        self.actor = None

    def get_parameters(self, location, rotation, manage_hits):
        if (location == FVector(0, 0, MAGICAL_VALUE)):
            self.location = FVector(
                random.uniform(-100, 100),
                random.uniform(200, 400),
                100 + random.uniform(-30, 80))
        else:
            self.location = location
        if (rotation == FRotator(0, 0, MAGICAL_VALUE)):
            self.rotation = FRotator(
                0,
                random.uniform(-15, 10),
                random.uniform(-30, 30))
        else:
            self.rotation = rotation
        self.manage_hits = manage_hits

    def set_parameters(self):
        self.set_location(self.location)
        self.set_rotation(self.rotation)
        self.hidden = False
        # manage OnActorBeginOverlap events
        if (self.manage_hits == True):
            self.actor.bind_event('OnActorBeginOverlap', self.manage_overlap)
            self.actor.bind_event('OnActorHit', self.on_actor_hit)

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

    def set_hidden(self, hidden):
        self.hidden = hidden
        self.actor.SetActorHiddenInGame(hidden)

    def get_status(self):
        status = defaultdict(list)
        status['actor'] = self.actor.get_name()
        status['location'].append(('x', self.location.x))
        status['location'].append(('y', self.location.y))
        status['location'].append(('z', self.location.z))
        status['rotation'].append(('pitch', self.rotation.pitch))
        status['rotation'].append(('roll', self.rotation.roll))
        status['rotation'].append(('yaw', self.rotation.yaw))
        status['hidden'] = self.hidden
        status['manage_hits'] = self.manage_hits
        return status
