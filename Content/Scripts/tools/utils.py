"""Defines general utility functions used by intphys"""

import os

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary


def intphys_root_directory():
    """Return the absolute path to the intphys root directory"""
    # guess it from the evironment variable first, or from the
    # relative path from here
    try:
        root_dir = os.environ['INTPHYS_ROOT']
    except:
        root_dir = os.path.join(os.path.dirname(__file__), '../..')

    # make sure the directory is the good one
    assert os.path.isdir(root_dir)
    assert 'intphys.py' in os.listdir(root_dir)

    return os.path.abspath(root_dir)


def exit_ue(world, message=None):
    """Quit the game, optionally displaying an error message

    `world` is the world reference from the running game

    """
    if message:
        ue.log_error(message)

    KismetSystemLibrary.QuitGame(world)
