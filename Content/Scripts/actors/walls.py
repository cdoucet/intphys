from actors.wall import Wall

"""
Walls is a wrapper class that make 3 walls spawn.
"""


class Walls():
    def __init__(self, world,
                 length=2000,
                 depth=1000,
                 height=1,
                 material=None,
                 overlap=False,
                 warning=False):
        self.get_parameters(length, depth, height, material, overlap, warning)
        self.front = Wall(world, "Front",
                          self.length, self.depth,
                          self.height, self.material, self.overlap, self.warning)
        self.right = Wall(world, "Right",
                          self.length, self.depth,
                          self.height, self.material, self.overlap, self.warning)

        self.left = Wall(world, "Left",
                          self.length, self.depth,
                          self.height, self.material, self.overlap, self.warning)

    def actor_destroy(self):
        self.front.actor_destroy()
        self.right.actor_destroy()
        self.left.actor_destroy()

    def get_parameters(self, length, depth, height, material, overlap, warning):
        self.depth = depth
        self.length = length
        self.height = height
        self.material = material
        self.overlap = overlap
        self.warning = warning

    def get_status(self):
        print(self.front.get_status())
        print(self.left.get_status())
        print(self.right.get_status())
        return None
