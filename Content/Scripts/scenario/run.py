import importlib
import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager


class Run:
    def __init__(self, world, saver, actors_params, status_header):
        self.world = world
        self.saver = saver
        self.actors_params = actors_params
        self.actors = None
        self.status_header = status_header

    def get_status(self):
        """Return the current status of each moving actor in the scene"""
        # TODO change actors in status : Camera ? Walls ? Floor ? SkySphere ? ect
        return {k: v.get_status() for k, v in self.actors.items()}

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
        self.saver.update_camera(self.actors['Camera'])

    def tick(self, tick_index):
        if (self.actors is not None):
            for actor_name, actor in self.actors.items():
                if 'object' in actor_name or 'occluder' in actor_name:
                    actor.move()


class RunCheck(Run):
    def __init__(self, world, saver, actors_params, status_header):
        super().__init__(world, saver, actors_params, status_header)
        self.visible_frame = []

    def tick(self, tick_index):
        super().tick(tick_index)
        if (self.actors is None):
            return
        magic_actor = self.actors[self.actors_params['magic']['actor']]
        ignored_actors = []
        for actor_name, actor in self.actors.items():
            if 'object' not in actor_name.lower() and 'occluder' not in actor_name.lower():
                if 'walls' in actor_name.lower():
                    ignored_actors.append(actor.front.actor)
                    ignored_actors.append(actor.left.actor)
                    ignored_actors.append(actor.right.actor)
                else:
                    ignored_actors.append(actor.actor)
        res = ScreenshotManager.IsActorInLastFrame(magic_actor.actor, ignored_actors)[0]
        self.visible_frame.append(res)

    def del_actors(self):
        super().del_actors()
        try:
            """
            occluders = []
            for actor_name, actor in self.actors.items():
                if 'occluder' in actor_name.lower():
                    occluders.append(actor)
            for item in self.visible_frame:
                if item[0] is False:
                    if 
                    return self.visible_frame.index(item)
            """
            return self.visible_frame.index(False)
        except:
            ue.log("Warning: the magic actor is never occluded in the check run")
            return -1


class RunPossible(Run):
    def tick(self, tick_index):
        super().tick(tick_index)
        ignored_actors = []
        self.saver.capture(ignored_actors, self.status_header, self.get_status())


class RunImpossible(Run):
    def tick(self, tick_index):
        super().tick(tick_index)
        ignored_actors = []
        if (self.actors[self.actors_params['magic']['actor']].hidden is True):
            ignored_actors.append(self.actors[self.actors_params['magic']['actor']].actor)
        self.saver.capture(ignored_actors, self.status_header, self.get_status())
