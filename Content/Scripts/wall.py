"""The wall surrounds the scene.

3 sub-walls in 3 directions (front, left and right). There is no wall
behind the camera to ensure the objects will not collide an invisible
wall.

"""

import unreal_engine as ue


class Wall:
    def __init__(self):
        ue.log('init enclosing wall')
