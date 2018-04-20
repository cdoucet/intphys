import importlib
import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager


class Run:
    def __init__(self, world, actors_params):
        self.world = world
        self.actors_params = actors_params
        self.actors = None

    def spawn_actors(self):
        self.actors = {}
        for actor, params in self.actors_params.items():
            if ('magic' in actor):
                continue
            if ('skysphere' in actor.lower()):
                class_name = 'SkySphere'
            else:
                class_name = actor.split('_')[0].title()
            # dynamically import and instantiate the class corresponding to the actor
            self.actors[actor] = getattr(importlib.import_module("actors.{}".format(actor.lower().split('_')[0])), class_name)(world=self.world, params=params)

    def del_actors(self):
        if (self.actors is not None):
            for actor_name, actor in self.actors.items():
                actor.actor_destroy()
            self.actors = None

    def play(self):
        self.spawn_actors()

    def tick(self, tick_index):
        if (self.actors is not None):
            for actor_name, actor in self.actors.items():
                if 'object' in actor_name or 'occluder' in actor_name:
                    actor.move()


class RunCheck(Run):
    def __init__(self, world, actors_params):
        super().__init__(world, actors_params)
        self.visible_frame = []

    def tick(self, tick_index):
        super().tick(tick_index)
        if (self.actors is None):
            return
        # TODO add the ignored actors array if needed
        actor = self.actors[self.actors_params['magic']['actor']].actor
        res = ScreenshotManager.IsActorInFrame(actor, tick_index)
        if (res is True):
            print("ta race --> {}".format(tick_index))
        self.visible_frame.append(res)

    def del_actors(self):
        super().del_actors()
        try:
            return self.visible_frame.index(False)
        except IndexError:
            ue.log("Error: Didn't find any true value in occluded_frame array")
            return -1


class RunPossible(Run):
    def tick(self, tick_index):
        super().tick(tick_index)


class RunImpossible(Run):
    pass
