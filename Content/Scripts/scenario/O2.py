"""Bloc O2 is change of shape. Spheres, cubes and cones."""
import random
from actors.object import Object
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from unreal_engine.classes import ScreenshotManager
from scenario.checkUtils import checks_time_laps
from scenario.checkUtils import remove_last_and_first_frames
from scenario.checkUtils import remove_invisible_frames
from scenario.checkUtils import separate_period_of_occlusions
from scenario.checkUtils import remove_frame_after_first_bounce
from scenario.checkUtils import store_actors_locations
from scenario.checkUtils import remove_frames_close_to_magic_tick
import unreal_engine as ue


class O2Base:
    @property
    def name(self):
        return 'O2'

    @property
    def description(self):
        return 'shape constancy'


class O2Train(O2Base, Train):
    pass


class O2Test(O2Base, MirrorTest):
    def __init__(self, world, saver, is_occluded, movement):
        super().__init__(world, saver, is_occluded, movement)
        self.check_array['visibility'] = [[], []]
        self.check_array['location'] = [[], []]
        self.check_array['grounded'] = [[], []]

    def generate_parameters(self):
        super().generate_parameters()
        magic_actor = self.params['magic']['actor']
        magic_mesh = self.params[magic_actor].mesh
        new_mesh = random.choice(
            [m for m in Object.shape.keys() if m != magic_mesh])
        self.params['magic']['mesh'] = new_mesh
        if 'dynamic' in self.movement:
            location = self.params[magic_actor].location
            self.params[magic_actor].initial_force.z = \
                3e4 + (abs(location.y) - 1500) * 4

    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        location = store_actors_locations(self.actors)
        self.check_array['location'][self.run].append(location)
        frame = (self.ticker / 2) - 0.5
        IsActorInFrame = ScreenshotManager.IsActorInFrame(magic_actor, frame)
        self.check_array['visibility'][self.run].append(IsActorInFrame)
        # check if the magic actor is in the air
        if (magic_actor.get_actor_location().z <= 100 +
                self.actors[self.params['magic']['actor']].scale.z * 50):
            grounded = True
        else:
            grounded = False
        self.check_array['grounded'][self.run].append(grounded)

    def setup_magic_actor(self):
        # on run 1 and 3 the magic actor mesh is
        # self.params[magic_actor].mesh at start, on runs 2 and 4 it
        # is self.params['magic']['mesh'] (runs 1, 2 are impossible,
        # runs 3, 4 are possible).
        run = self.run + 1
        is_magic_mesh = True if run in (2, 4) else False
        magic_actor_type = self.params['magic']['actor']
        magic_actor = self.actors[magic_actor_type]
        new_mesh = (self.params['magic']['mesh'] if is_magic_mesh
                    else self.params[magic_actor_type].mesh)
        magic_actor.set_mesh_str(Object.shape[new_mesh])

    def static_visible(self):
        visibility_array = \
            checks_time_laps(self.check_array["visibility"], True)
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = \
            checks_time_laps(self.check_array["visibility"], True)
        grounded_array = \
            checks_time_laps(self.check_array["grounded"], False)
        # check if the actor is visible AND up in the air
        final_array = []
        grounded_array = remove_frame_after_first_bounce(grounded_array)
        visibility_array = remove_last_and_first_frames(visibility_array, 8)
        for frame in grounded_array:
            if frame in visibility_array:
                final_array.append(frame)
        self.params['magic']['tick'] = random.choice(final_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = \
            checks_time_laps(self.check_array["visibility"], True)
        grounded_array = \
            checks_time_laps(self.check_array["grounded"], False)
        grounded_array = remove_frame_after_first_bounce(grounded_array)
        visibility_array = remove_last_and_first_frames(visibility_array, 5)
        final_array = []
        # check if the actor is visible AND up in the air
        for frame in grounded_array:
            if frame in visibility_array:
                final_array.append(frame)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(final_array))
        final_array = \
            remove_frames_close_to_magic_tick(final_array,
                                              self.params['magic']['tick'][0],
                                              5)
        self.params['magic']['tick'].append(random.choice(final_array))
        self.params['magic']['tick'].sort()
        ue.log("magic_tick {} and {}".format(self.params['magic']['tick'][0], self.params['magic']['tick'][1]))
        return True

    def static_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array['visibility'], False)
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array["visibility"], False)
        grounded_array = \
            checks_time_laps(self.check_array["grounded"], False)
        grounded_array = remove_frame_after_first_bounce(grounded_array)
        visibility_array = remove_invisible_frames(visibility_array)
        # check if the actor is visible AND up in the air
        final_array = []
        for frame in grounded_array:
            if frame in visibility_array:
                final_array.append(frame)
        self.params['magic']['tick'] = random.choice(final_array)
        return True

    def dynamic_2_occluded(self):
        visibility_array = \
            checks_time_laps(self.check_array["visibility"], False)
        grounded_array = \
            checks_time_laps(self.check_array["grounded"], False)
        grounded_array = remove_frame_after_first_bounce(grounded_array)
        visibility_array = remove_invisible_frames(visibility_array)
        occlusions = separate_period_of_occlusions(visibility_array)
        for occlusion in occlusions:
            temp_array = occlusion
            for frame in temp_array:
                if frame not in grounded_array:
                    occlusion.remove(frame)
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusions[0]))
        self.params['magic']['tick'].append(random.choice(occlusions[1]))
        return True
