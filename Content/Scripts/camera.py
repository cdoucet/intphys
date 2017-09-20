"""The camera.py module models the camera behavior.

"""

import unreal_engine as ue


class Camera:
    def begin_play(self):
        self.camera = self.uobject.get_owner()
        print(self.camera.get_name())
        print(self.uobject.get_name())

    def on_actor_begin_overlap(self, me, other_actor):
        raise RuntimeError(
            'Overlap detected between {} and {}',
            me.uobject.get_name(), other_actor.uobject.get_name())
