"""Defines utilities functions used by intphys"""

import unreal_engine as ue
from unreal_engine.classes import KismetSystemLibrary


def exit_ue(world, message=None):
    """Quit the game, optionally displaying an error message"""
    if message:
        ue.log_error(message)

    KismetSystemLibrary.QuitGame(world)
