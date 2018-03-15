"""Python interface to load materials from Content/Materials"""

import os
import random

import unreal_engine as ue
from unreal_engine.classes import Material

from tools.utils import intphys_root_directory


def get_material_path(path):
    """Convert the `path` to a material asset to its name in UE conventions"""
    base_path = os.path.splitext('/Game/' + path.split('/Content/')[1])[0]
    return base_path + '.' + os.path.basename(base_path)


def load_materials(path):
    """Return the list of materials found in `path` following UE conventions

    `path` must be relative to the 'intphys/Content' directory

    """
    materials_dir = os.path.join(intphys_root_directory(), 'Content', path)
    if not os.path.isdir(materials_dir):
        raise ValueError('directory not found: {}'.format(materials_dir))

    return [get_material_path(os.path.join(materials_dir, f))
            for f in os.listdir(materials_dir) if f.endswith('.uasset')]


def get_random_material(materials):
    """Return a random element from a list"""
    random.shuffle(materials)
    return materials[0]


def get_random_material_for_category(name):
    return get_random_material(load_materials('Materials/' + name))
