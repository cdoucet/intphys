import random

from unreal_engine import FVector, FRotator

from scenario import base_scenario
from actors.parameters import ObjectParams, OccluderParams
from tools.materials import get_random_material


class SandBox(base_scenario.BaseTest):
    @property
    def name(self):
        return 'SandBox'

    is_magic_actor_hidden = False

    def get_nchecks(self):
        return 1 if self.is_occluded else 0

    def generate_parameters(self):
        params = super().generate_parameters()
        params[f'object_{1}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=FVector(1000, 0, 0),
                rotation=FRotator(0, 0, 0),
                scale=FVector(1, 1, 1),
                mass=100,
                force=FVector(0, 1e8, 0),
                overlap=True)
        params[f'object_{2}'] = ObjectParams(
                mesh='Sphere',
                material=get_random_material('Object'),
                location=FVector(1000, 800, 0),
                rotation=FRotator(0, 0, 0),
                scale=FVector(1, 1, 1),
                mass=100,
                overlap=True)
        """
        params['occluder'] = OccluderParams(
                material=get_random_material('Wall'),
                location=FVector(400, -500, 0),
                rotation=FRotator(0, 0, 90),
                scale=FVector(1, 1, 1),
                moves=[0, 100, 145],
                speed=1)
        """
        params['magic'] = {
            'actor': f'object_{1}',
            'tick': 50}        
        return params

    def setup_magic_trick(self, actor, run):
        print("begin magic trick")
        #actor.set_force(FVector(1e8, 0, 0))
        
    def apply_magic_trick(self, actor, run):
        print("end magic trick")

    def get_nruns(self):
        return 1
