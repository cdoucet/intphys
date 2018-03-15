import random

import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.enums import ECameraProjectionMode


def get_actor_class(name):
    from actors.floor import Floor
    from actors.light import Light
    from actors.object import Object
    from actors.occluder import Occluder
    from actors.walls import Walls

    name = name.lower()
    if 'camera' in name:
        return Camera
    elif 'floor' in name:
        return Floor
    elif 'light' in name:
        return Light
    elif 'object' in name:
        return Object
    elif 'occluder' in name:
        return Occluder
    elif 'walls' in name:
        return Walls
    else:
        raise ValueError('actor class unknown for {}'.format(name))


class Scene(object):
    """The scene renders a given `scenario` in a given `world`

    A scene is made of several runs. Train scenes are always a single
    run. Test scenes have 4 runs plus some check runs. The number of
    checks varies accross scenarii.

    Parameters
    ----------
    world: ue.uobject
       The game world in which to render the scene
    scenario: child of scenario.base.Base
        The scenario to execute. A scenario defines the actors,
        generates parameters for them and implement the magic tricks.

    """
    def __init__(self, world, scenario):
        self.world = world
        self.scenario = scenario
        self.current_run = 0

        self.params = self.scenario.generate_parameters()
        self.actors = {
            k: get_actor_class(k)(world=self.world, params=v)
            for k, v in self.params.items()}

    def get_nruns_remaining(self):
        """Return the number of runs to render before the end of the scene"""
        return self.scenario.get_nruns() - self.current_run

    def description(self):
        return self.scenario.get_description()

    def render(self):
        """Setup the actors defined by the scenario to their initial state"""
        # replace the actors to their initial position
        self._reset()

        # update the run index
        self.current_run += 1

        # setup the magic actor before applying the magic trick
        self.scenario.magic_setup(self.current_run)

    def clear(self):
        """Destroy all the actors in the scene"""
        for k, v in self.actors.items():
            v.actor_destroy()
        self.actors = {}

    def get_status(self):
        """Return the current status of each actor in the scene"""
        return {k: v.get_status() for k, v in self.actors}

    def is_valid(self):
        """Return True when the scene is in valid state

        A scene can be invalid if some forbidden hit occured (e.g. an
        occluder overlapping the camera), or , for test scenes, if a
        check run failed.

        """
        # TODO
        return True

    def is_check_run(self):
        """Return True if the current run is a check"""
        if (not self.scenario.is_train() and
            self.current_run <= self.scenario.get_nchecks()):
            return True
        else:
            return False

    def moving_actors(self):
        """Return the dict of moving actors (objects and occluders)"""
        return {
            k: v for k, v in self.actors.items()
            if 'occluder' in k or 'object' in k}

    def _spawn(self):
        """Spawn and initialize all the actors"""
        pass

    def _reset(self):
        """Set all the actors to their initial location/rotation"""
        for k, v in self.moving_actors().items():
            v.set_location(self.params[k].location)
            v.set_rotation(self.params[k].rotation)
