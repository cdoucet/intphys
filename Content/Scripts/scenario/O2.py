"""Bloc O2 is change of shape. Spheres, cubes and cones."""
import random
from actors.object import Object
from scenario.mirrorTest import MirrorTest
from scenario.train import Train
from unreal_engine.classes import Friction, ScreenshotManager
from unreal_engine import FVector
import unreal_engine as ue


class O2Base:
    @property
    def name(self):
        return 'O2'

    @property
    def description(self):
        return 'bloc O2'


class O2Train(O2Base, Train):
    def __init__(self, world, saver):
        super().__init__(world, saver)

    def generate_parameters(self):
        super().generate_parameters()

        for name, params in self.params.items():
            if 'object' in name:
                # objects can be of any shapes, not only sphere
                params.mesh = random.choice(list(Object.shape.keys()))


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

    def fill_check_array(self):
        magic_actor = self.actors[self.params['magic']['actor']].actor
        location = FVector()
        location.x = int(round(magic_actor.get_actor_location().x))
        location.y = int(round(magic_actor.get_actor_location().y))
        location.z = int(round(magic_actor.get_actor_location().z))
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
        Friction.SetMassScale(magic_actor.get_mesh(), 1)
        if 'Cube' in magic_actor.mesh_str:
            Friction.SetMassScale(magic_actor.get_mesh(), 0.6155297517867)
        elif 'Cone' in magic_actor.mesh_str:
            Friction.SetMassScale(magic_actor.get_mesh(), 1.6962973279499)

    """
    def apply_magic_trick(self):
        # swap the mesh of the magic actor
        magic_actor = self.actors[self.params['magic']['actor']]
        current_mesh = magic_actor.mesh_str.split('.')[-1]
        mesh_1 = self.params['magic']['mesh']
        mesh_2 = self.params[self.params['magic']['actor']].mesh
        new_mesh = mesh_1 if current_mesh == mesh_2 else mesh_2
        magic_actor.set_mesh_str(Object.shape[new_mesh])
    """

    def static_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array["visibility"], True)
        try:
            for frame in range(5):
                visibility_array.remove(visibility_array[0])
                visibility_array.remove(visibility_array[-1])
        except IndexError:
            pass
        if len(visibility_array) < 1:
            ue.log_warning("not enough occluded frame")
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array["visibility"], True)
        grounded_array = \
            self.checks_time_laps(self.check_array["grounded"], False)
        # check if the actor is visible AND up in the air
        final_array = []
        try:
            for frame in range(5):
                visibility_array.remove(visibility_array[0])
                visibility_array.remove(visibility_array[-1])
        except IndexError:
            pass
        for frame in grounded_array:
            if frame in visibility_array:
                final_array.append(frame)
        if len(final_array) < 1:
            ue.log_warning("not enough occluded frame")
            return False
        self.params['magic']['tick'] = random.choice(final_array)
        return True

    def dynamic_2_visible(self):
        visibility_array = \
            self.checks_time_laps(self.check_array["visibility"], True)
        try:
            for frame in range(5):
                visibility_array.remove(visibility_array[0])
                visibility_array.remove(visibility_array[-1])
        except IndexError:
            pass
        grounded_array = \
            self.checks_time_laps(self.check_array["grounded"], False)
        # check if the actor is visible AND up in the air
        final_array = []
        for frame in grounded_array:
            if frame in visibility_array:
                final_array.append(frame)
        # if the number of frame where the magic actor is not grounded is less
        # than 4 time the number of magic tick required, scene will restart
        if len(final_array) < 8:
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(final_array))
        final_array.remove(self.params['magic']['tick'][0])
        self.params['magic']['tick'].append(random.choice(final_array))
        self.params['magic']['tick'].sort()
        return True

    def static_occluded(self):
        visibility_array = \
            self.checks_time_laps(self.check_array['visibility'], False)
        # if the number of frame where the magic actor is visible is less than
        # 4 time the number of magic tick required, scene need to be restarted
        if len(visibility_array) < 1:
            return False
        self.params['magic']['tick'] = random.choice(visibility_array)
        return True

    def dynamic_1_occluded(self):
        visibility_array = \
            self.checks_time_laps(self.check_array["visibility"], False)
        grounded_array = \
            self.checks_time_laps(self.check_array["grounded"], False)
        # remove the last occurences of not visible actor if
        # it is out of the fieldview
        first = 0
        last = 99
        try:
            while True:
                quit = False
                if visibility_array[0] == first:
                    visibility_array.remove(first)
                    first += 1
                else:
                    quit = True
                if visibility_array[-1] == last:
                    visibility_array.remove(last)
                    last -= 1
                elif quit is True:
                    break
        except IndexError:
            pass
        # check if the actor is visible AND up in the air
        final_array = []
        for frame in grounded_array:
            if frame in visibility_array:
                final_array.append(frame)
        # if the number of frame where the magic actor is not grounded is less
        # than 4 time the number of magic tick required, scene will restart
        if len(final_array) < 1:
            ue.log_warning("Not enough final choices")
            return False
        self.params['magic']['tick'] = random.choice(final_array)
        return True

    def dynamic_2_occluded(self):
        visibility_array = \
            self.checks_time_laps(self.check_array["visibility"], False)
        grounded_array = \
            self.checks_time_laps(self.check_array["grounded"], False)
        # remove the last and the first occurences of not visible actor if
        # it is out of the fieldview
        first = 0
        last = 99
        try:
            while True:
                quit = False
                if visibility_array[0] == first:
                    visibility_array.remove(first)
                    first += 1
                else:
                    quit = True
                if visibility_array[-1] == last:
                    visibility_array.remove(last)
                    last -= 1
                elif quit is True:
                    break
        except IndexError:
            pass
        occlusion = []
        occlusion.append([])
        temp_array = visibility_array
        if len(temp_array) < 2:
            ue.log_warning("not enough occluded frame")
            return False
        previous_frame = temp_array[0] - 1
        i = 0
        # distinguish the different occlusion time laps
        for frame in temp_array:
            if frame - 1 != previous_frame:
                i += 1
                occlusion.append([])
            if frame in grounded_array:
                occlusion[i].append(frame)
            previous_frame = frame
        # if there is less than 2 distinct occlusion the scene will restart
        # same if there is less than 2 frame where the actor is not grounded
        # in each occlusion
        if (len(occlusion) < 2 or
                len(occlusion[0]) == 0 or
                len(occlusion[1]) == 0):
            ue.log_warning("not enough occluded frame")
            return False
        self.params['magic']['tick'] = []
        self.params['magic']['tick'].append(random.choice(occlusion[0]))
        self.params['magic']['tick'].append(random.choice(occlusion[1]))
        return True
