from dataclasses import dataclass, field
from unreal_engine import FVector, FRotator
from unreal_engine.enums import ECameraProjectionMode


@dataclass
class CameraParams:
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    field_of_view: float = 90
    aspect_ratio: float = 1
    projection_mode: int = ECameraProjectionMode.Perspective


@dataclass
class FloorParams:
    material: str = None
    scale: FVector = FVector(100, 100, 1)
    friction: float = 0.5
    restitution: float = 0.5


@dataclass
class LightParams:
    location: FVector = FVector(0, 0, 0)
    rotation: FRotator = FRotator(0, 0, 0)
    type: str = 'SkyLight'


@dataclass
class WallsParams:
    material: str = None
    length: float = 2000
    depth: float = 1000
    height: float = 1


@dataclass
class ObjectParams:
    mesh: str
    material: str
    location: FVector
    rotation: FRotator
    scale: FVector = FVector(1, 1, 1)
    mass: float = 1
    friction: float = 0.5
    restitution: float = 0.5
    force: FVector = FVector(0, 0, 0)


@dataclass
class OccluderParams:
    material: str
    location: FVector
    rotation: FRotator
    scale: FVector = FVector(1, 1, 1)
    moves: tuple = (0)
    speed: float = 1
