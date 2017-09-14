import unreal_engine as ue


class Camera:
    def on_actor_begin_overlap(self, me, other_actor):
        raise RuntimeError(
            'Overlap detected between {} and {}',
            me.uobject.get_name(), other_actor.get_name())
