"""The scene's floor"""

import random

import unreal_engine as ue
from unreal_engine.classes import Material, StaticMesh


class Floor:
    materials = ue.get_assets('/Game/Materials/Floor')

    def __init__(self):
        ue.log('init floor')

        # choose a random material
        m = self.materials
        random.shuffle(m)
        self.material = m[0]

    def begin_play(self):
        self.actor = self.uobject.get_owner()
        self.actor.set_actor_location(0, -720, 0)
        self.actor.set_actor_scale(5, 5, 1)
        self.actor.set_actor_rotation(0, 0, 0)

        mesh = self.actor.get_actor_component_by_type(
            ue.find_class('StaticMeshComponent'))
        mesh.SetStaticMesh(
            ue.load_object(StaticMesh, '/Game/Meshes/Floor_400x400'))
        mesh.set_material(0, self.material)

        ue.log('begin play {}'.format(self.actor.get_name()))
