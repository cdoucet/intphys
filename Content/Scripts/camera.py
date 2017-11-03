"""This module manages the scene's camera.

It defines and controls it's location and rotation.

The other camera parameters are constant and fixed in UE:
- a perspective projection,
- a ratio heigth/width fixed at 1 (to nsure a square image),
- an horizontal field of view of 90 degrees.
TODO implement this in Python

"""

import random

from unreal_engine import FVector, FRotator
from unreal_engine.classes import PyActor
import unreal_engine as ue
import os
import png
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize
from unreal_engine import FColor

class CameraPythonComponant:
    def __init__(self):
        self.location, self.rotation = self.get_test_parameters()

    @staticmethod
    def get_train_parameters():
        """Returns random coordinates for train scenes

        In train scenes, camera has a high variability. Only the roll
        is forced to 0.

        """
        location = FVector(
            random.uniform(-100, 100),
            random.uniform(200, 400),
            100 + random.uniform(-30, 80))

        rotation = FRotator(
            random.uniform(-30, 30),
            random.uniform(-15, 10),
            0)

        return location, rotation

    @staticmethod
    def get_test_parameters():
        """Returns random coordinates for test scenes

        In test scenes, the camera has a constrained location, with
        little variations along the y axis and pitch.

        """
        location = FVector(
            0,
            -100 * random.random(),
            150)

        rotation = FRotator(
            0,
            -10 * random.random(),
            0)

        return location, rotation

    def begin_play(self):
        # retrieve the camera object from its Python component
        self.actor = self.uobject.get_owner()

        # OnActorBeginOverlap events are redirected to the
        # manage_overlap method
        self.actor.bind_event(
            'OnActorBeginOverlap', self.manage_overlap)

        # place the camera at the desired coordinates
        self.actor.set_actor_location(self.location)
        self.actor.set_actor_rotation(self.rotation)

    def tick(self, delta_time):
        print delta_time
        size = IntSize(288, 288) # this line let size.X and size.Y with a null value... can't say why
        size.X = 288
        size.Y = 288
        self.takeScreenshot(size)

    def manage_overlap(self, me, other):
        """Raises a Runtime error when some actor overlaps the camera"""
        message = 'Camera overlapping {}'.format(other.get_name())
        ue.log_error(message)

    def get_status(self):
        """Returns the camera coordinates as a string"""
        location = self.uobject.get_actor_location()
        rotation = self.uobject.get_actor_rotation()

        return ' '.join(
            location.x, location.y, location.z,
            rotation.pitch, rotation.yaw, rotation.roll)

    def savePNG(self, pixel_array, size, flag):
        if (len(pixel_array) == 0):
            print "savePNG failed. The array of pixels is empty"
            return False
        png_pixels = []
        index = 0
        for y in range(0, size.Y):
            line = []
            for x in range(0, size.X):
                line.append([pixel_array[index], pixel_array[index + 1], pixel_array[index + 2]])
                index += 3
            png_pixels.append(line)
        path = os.environ['MYPROJECT'] + "/Test_pictures/"
        if os.path.isdir(path) == False:
            os.makedirs(path)
            print "--> 'Test_pictures' directory created"
        pic_name = testScreenshot.BuildFileName(flag)
        png.from_array(png_pixels, 'RGB').save(path + pic_name)
        print "--> picture '" + pic_name + "' saved in " + path
        return True

    def takeDepthAndMask(self, size, stride, origin, objects, ignoredObjects):
        return True

    def takeScreenshot(self, size):
        print "--> beginning of the screenshot script"
        print "size = X->", size.X, " Y->", size.Y
        pixel_array = []
        pixel_array = testScreenshot.CaptureScreenshot(size, pixel_array)
        if (len(pixel_array) == 0):
            print "takeScreenshot failed. The array of pixels is empty"
            return False
        self.savePNG(pixel_array, size, 1)
        print "--> end of the screenshot script"
        return True

    def doTheWholeStuff(self, size, stride, origin, objects, ignoredObjects):
        if self.takeScreenshot(size) == False:
            print "takeScreenshot failed"
            return False
        if self.takeDepthAndMask(size, stride, origin, objects, ignoredObjects) == False:
            print "takeDepthAndMask failed"
            return False
        return True
        
    def salut(self):
        print "salut!"
