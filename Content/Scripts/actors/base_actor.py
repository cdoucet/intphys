import unreal_engine as ue
from collections import defaultdict

"""BaseActor is the very base of the actors inheritance tree

It is the base class of every python component build with an actor
(all of them, though).  Beware : this is a recursive instantiation
(see comments at the begining of other classes) Therefore, don't try
to use the self.actor before the actor_spawn function is called

"""


class BaseActor():
    """
    __init__ instantiate the class
    parameters ->
    actor: spawned actor (UObject)
    location: location of the actor (FVector). Default value: 0, 0, 0
    rotation: rotation of the actor (FRotator). Default value: 0, 0, 0
    """
    def __init__(self, actor=None):
        self.actor = actor

    def actor_destroy(self):
        if (self.actor is not None):
            self.actor.actor_destroy()
            self.actor = None
        self.actor = None

    def get_parameters(self, location, rotation, overlap, warning):
        self.location = location
        self.rotation = rotation
        self.overlap = overlap
        self.warning = warning

    def set_parameters(self):
        self.set_location(self.location)
        self.set_rotation(self.rotation)
        self.hidden = False

        # manage OnActorBeginOverlap events
        if self.warning and self.overlap:
            self.actor.bind_event('OnActorBeginOverlap', self.manage_overlap)
        if self.warning and not self.overlap:
            self.actor.bind_event('OnActorHit', self.on_actor_hit)

    """
    this getter is important : in the recursive instance,
    it's an internal unreal engine function called get_actor which is called
    so wherever you call get_actor(), it will works
    """
    def get_actor(self):
        return self.actor

    def set_actor(self, actor):
        self.actor = actor

    def set_location(self, location):
        self.location = location
        if not self.actor.set_actor_location(self.location, False):
            ue.log_warning("Failed to set the location of an actor")

    def set_rotation(self, rotation):
        self.rotation = rotation
        if not self.actor.set_actor_rotation(self.rotation):
            ue.log_warning(
                "Failed to set the rotation of {}"
                .format(self.actor.get_name()))

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps this object"""
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
        status['overlap'] = self.overlap
        status['warning'] = self.warning
        return status
