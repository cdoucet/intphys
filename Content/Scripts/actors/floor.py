"""The scene's floor"""

import random
import unreal_engine as ue

from abstract_actor import BaseActor


class Floor(BaseActor):
    floor_materials = ue.get_assets('/Game/Materials/Floor')

    def __init__(self):
        super(Floor, self).__init__(params)
        self.params['mesh'] = '/Game/Meshes/Floor_400x400'
        self.params['material'] = random.shuffle(self.floor_materials)[0]

    def begin_play(self):
        super(Floor, self).begin_play()

        actor = self.get_actor()
        actor.set_actor_location(0, -720, 0)
        actor.set_actor_scale(5, 5, 1)
        actor.set_actor_rotation(0, 0, 0)

        mesh = actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))
        mesh.SetStaticMesh(
            ue.load_object(StaticMesh, ))
        mesh.set_material(0, self.material)
