import importlib
import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager
from unreal_engine.classes import Friction


class Run:
    def __init__(self, world, saver, actors_params, status_header, is_test):
        self.world = world
        self.saver = saver
        self.actors_params = actors_params
        self.actors = None
        self.status_header = status_header
        self.ticker = 0
        self.check_array = []
        self.b_is_valid = True
        self.is_test = is_test

    def get_status(self):
        """Return the current status of each moving actor in the scene"""
        # TODO change actors appearing in status :
        # Camera ? Walls ? Floor ? SkySphere ? ect.
        if self.actors is not None:
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
            self.actors[actor] = getattr(module, class_name)(
                world=self.world, params=params)

            if 'object' in actor.lower():
                # if 'Sphere' in self.actors[actor].mesh_str:
                #    Friction.SetMassScale(self.actors[actor].get_mesh(), 1)
                if 'Cube' in self.actors[actor].mesh_str:
                    Friction.SetMassScale(self.actors[actor].get_mesh(),
                                          0.6155297517867)
                elif 'Cone' in self.actors[actor].mesh_str:
                    Friction.SetMassScale(self.actors[actor].get_mesh(),
                                          1.6962973279499)

    def play(self):
        self.spawn_actors()
        self.saver.update_camera(self.actors['Camera'])

    def is_valid(self):
        return all([a.is_valid for a in self.actors.values()])

    def tick(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                if 'object' in actor_name or 'occluder' in actor_name:
                    actor.move()

        self.ticker += 1

        if self.actors is None:
            return

        if self.is_test is False:
            return

        magic_actor = self.actors[self.actors_params['magic']['actor']].actor

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

        visible = ScreenshotManager.IsActorInLastFrame(
            magic_actor, ignored_actors)[0]

        if magic_actor.get_actor_location().z <= 100:
            grounded = True
        else:
            grounded = False

        temp = [visible, grounded]
        self.check_array.append(temp)

    def del_actors(self):
        if self.actors is not None:
            for actor_name, actor in self.actors.items():
                actor.actor_destroy()
            self.actors = None
        return self.check_array

    def capture(self):
        ignored_actors = []
        if self.actors[self.actors_params['magic']['actor']].hidden:
            ignored_actors.append(self.actors[self.actors_params['magic']['actor']].actor)
        self.saver.capture(ignored_actors,
                           self.status_header,
                           self.get_status())


# class RunImpossible(Run):
#     def capture(self):
#         ignored_actors = []
#         magic_actor = self.actors[self.actors_params['magic']['actor']]
#         if (magic_actor.hidden is True):
#             ignored_actors.append(magic_actor.actor)
#         self.saver.capture(ignored_actors,
#                            self.status_header,
#                            self.get_status())
