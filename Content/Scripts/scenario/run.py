import importlib
import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager
from unreal_engine.classes import Friction


class Run:
    def __init__(self, world, saver, actors_params, status_header):
        self.world = world
        self.saver = saver
        self.actors_params = actors_params
        self.actors = None
        self.status_header = status_header
        self.ticker = 0

    def get_status(self):
        """Return the current status of each moving actor in the scene"""
        # TODO change actors appearing in status :
        # Camera ? Walls ? Floor ? SkySphere ? ect.
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
            # dynamically import and instantiate
            # the class corresponding to the actor
            module_path = "actors.{}".format(actor.lower().split('_')[0])
            module = importlib.import_module(module_path)
            inst = getattr(module, class_name)(world=self.world, params=params)
            # just doing this to avoid make a line more than 80 caracters
            self.actors[actor] = inst
            if 'object' in actor.lower():
                # if 'Sphere' in self.actors[actor].mesh_str:
                #    Friction.SetMassScale(self.actors[actor].get_mesh(), 1)
                if 'Cube' in self.actors[actor].mesh_str:
                    Friction.SetMassScale(self.actors[actor].get_mesh(),
                                          0.6155297517867)
                elif 'Cone' in self.actors[actor].mesh_str:
                    Friction.SetMassScale(self.actors[actor].get_mesh(),
                                          1.6962973279499)

    def del_actors(self):
        if (self.actors is not None):
            for actor_name, actor in self.actors.items():
                actor.actor_destroy()
            self.actors = None

    def play(self):
        self.spawn_actors()
        self.saver.update_camera(self.actors['Camera'])

    def tick(self):
        if (self.actors is not None):
            for actor_name, actor in self.actors.items():
                if 'object' in actor_name or 'occluder' in actor_name:
                    actor.move()
        self.ticker += 1

    def is_valid(self):
        return all([a.is_valid for a in self.actors.values()])


class RunCheck(Run):
    def __init__(self, world, saver, actors_params, status_header):
        super().__init__(world, saver, actors_params, status_header)
        self.visible_frame = []

    def tick(self):
        super().tick()
        if (self.actors is None):
            return
        magic_actor = self.actors[self.actors_params['magic']['actor']]
        ignored_actors = []
        for actor_name, actor in self.actors.items():
            if 'object' not in actor_name.lower() and \
                    'occluder' not in actor_name.lower():
                if 'walls' in actor_name.lower():
                    ignored_actors.append(actor.front.actor)
                    ignored_actors.append(actor.left.actor)
                    ignored_actors.append(actor.right.actor)
                else:
                    ignored_actors.append(actor.actor)
        res = ScreenshotManager.IsActorInLastFrame(magic_actor.actor,
                                                   ignored_actors)[0]
        self.visible_frame.append(res)
        print(self.ticker)
        print(res)
        if (self.ticker > 1 and self.visible_frame[self.ticker - 2] != res):
            ue.log("tick {}: actor becomes {}".format(self.ticker,
                   'occluded' if res is False else 'non occluded'))

    def process_visibility(self):
        res = []
        # visible_in_first_frame = self.visible_frame[0]
        for frame_index in range(len(self.visible_frame) - 1):
            if (frame_index > 0 and
                    self.visible_frame[frame_index - 1] !=
                    self.visible_frame[frame_index]):
                res.append(frame_index)
        return res
        # return self.visible_frame.index(False) + 1

    def del_actors(self):
        super().del_actors()
        try:
            return self.process_visibility()
        except ValueError:
            ue.log("Warning: the magic actor is never \
                    occluded in the check run")
            return -1

    def capture(self):
        ignored_actors = []
        self.saver.capture(ignored_actors,
                           self.status_header,
                           self.get_status())

class RunPossible(Run):
    def capture(self):
        ignored_actors = []
        self.saver.capture(ignored_actors,
                           self.status_header,
                           self.get_status())


class RunImpossible(Run):
    def capture(self):
        ignored_actors = []
        magic_actor = self.actors[self.actors_params['magic']['actor']]
        if (magic_actor.hidden is True):
            ignored_actors.append(magic_actor.actor)
        self.saver.capture(ignored_actors,
                           self.status_header,
                           self.get_status())
