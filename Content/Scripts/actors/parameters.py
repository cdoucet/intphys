from dataclasses import dataclass, field

from unreal_engine import FVector, FRotator
from unreal_engine.enums import ECameraProjectionMode


@dataclass
class CameraParams:
    location: FVector
    rotation: FRotator
    field_of_view: float = 90
    aspect_ratio: float = 1
    projection_mode: int = ECameraProjectionMode.Perspective


@dataclass
class FloorParams:
    material: str
    scale: FVector = FVector(100, 100, 1)
    friction: float = 0.5
    restitution: float = 0.5


@dataclass
class LightParams:
    location: FVector
    rotation: FRotator
    type: str = 'SkyLight'


@dataclass
class WallsParams:
    material: str
    length: float = 2000
    depth: float = 1000
    height: float = 1
