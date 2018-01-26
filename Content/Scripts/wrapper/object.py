import unreal_engine as ue
from unreal_engine import FVector, FRotator
from unreal_engine.classes import Material, StaticMesh
from unreal_engine.enums import ECollisionChannel
from baseActor import BaseActor

class Object(BaseActor):
    def __init__(self, location, rotation):
        BaseActor.__init__(self, location, rotation)
        self.mesh = '/Engine/EngineMeshes/Sphere.Sphere'
        self.material = None
        self.scale = FVector(1, 1, 1)
        self.mass = 1.0
        self.force = FVector(-1e2, 0.0, 0.0)
