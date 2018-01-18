"""Take screenshots of raw scene, depth field and object masks"""

import os
import png

import unreal_engine as ue
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize
from unreal_engine import FColor


class Screenshot:
    def __init__(self, res_x, res_y):
        self.size = IntSize()
        self.size.X = res_x
        self.size.Y = res_y

        self.screenshots = []

    def take_screenshot(self):
        pixel_array = []
        pixel_array = testScreenshot.CaptureScreenshot(self.size)
        if (len(pixel_array) == 0):
            ue.log_error("take screenshot failed. The array of pixels is empty")
            return False
        if (len(pixel_array) != self.size.X * self.size.Y * 3):
            print("savePNG failed. The length of the array of pixel is wrong")
            return False

        # ue.log('screenshot took {} pixels'.format(len(pixel_array)))
        self.screenshots.append(pixel_array)
        return True

    def save(self, path):
        """Save the captured images as PNG in `path`"""
        ue.log('saving {} screenshots to {}'.format(
            len(self.screenshots), path))

        if not os.path.isdir(path):
            os.makedirs(path)

        for n, img in enumerate(self.screenshots):
            self._save_png(img, os.path.join(path, 'scene_{}.png'.format(n)))

    def _save_png(self, img, filename):
        ue.log('saving {}'.format(filename))
        png_pixels = []
        for y in range(0, self.size.Y):
            line = []
            for x in range(0, self.size.X):
                pixel = (y * self.size.X + x) * 3
                line.append([img[pixel], img[pixel + 1], img[pixel + 2]])
            png_pixels.append(line)

        png.from_array(png_pixels, 'RGB').save(filename)



# pixel_array is an array of integers. Every group of 3 values is a
# pixel with R, G and B value flag argument is an integer used to
# build the filename to know if it is a screenshot (1), a depth (2) or
# a mask (3)
def savePNG(pixel_array, size, flag):
    if (len(pixel_array) == 0):
        print("savePNG failed. The array of pixel is empty")
        return False
    if (len(pixel_array) != size.X * size.Y * 3):
        print("savePNG failed. The length of the array of pixel is wrong")
        return False

    png_pixels = []
    for y in range(0, size.Y):
        line = []
        for x in range(0, width):
            pixel = pixel_array[y * width + x]
            line.append([pixel.r, pixel.g, pixel.b])

        png_pixels.append(line)

    path = os.environ['MYPROJECT'] + "/Test_pictures/"
    if os.path.isdir(path) == False:
        os.makedirs(path)
        print("--> 'Test_pictures' directory created")

    pic_name = testScreenshot.BuildFileName(flag)
    png.from_array(png_pixels, 'RGB').save(path + pic_name)
    #print("--> picture '" + pic_name + "' saved in " + path)
    return True

# def takeDepth(size, stride, origin, objects, ignoredObjects):
#     #print("--> beginning of the depth script")
#     pixel_array = []
#     pixel_array = testScreenshot.CaptureDepth(size, stride, origin, objects, ignoredObjects)
#     if (len(pixel_array) == 0):
#         print("takeDepth failed. The array of pixels is empty")
#         return False
#     savePNG(pixel_array, size, 2)
#     #print("--> end of the depth script")
#     return True

# def takeMask(size, stride, origin, objects, ignoredObjects):
#     #print("--> beginning of the mask script")
#     pixel_array = []
#     pixel_array = testScreenshot.CaptureMask(size, stride, origin, objects, ignoredObjects)
#     if (len(pixel_array) == 0):
#         print("takeMask failed. The array of pixels is empty")
#         return False
#     savePNG(pixel_array, size, 3)
#     #print("--> end of the mask script")
#     return True

# def takeScreenshot(size):
#     #print("--> beginning of the screenshot script")
#     #print("given size = X->", size.X, " Y->", size.Y)
#     pixel_array = []
#     pixel_array = testScreenshot.CaptureScreenshot(size)
#     if (len(pixel_array) == 0):
#         ue.log_error("takeScreenshot failed. The array of pixels is empty")
#         return False
#     savePNG(pixel_array, size, 1)
#     #print("--> end of the screenshot script")
#     return True

# def doTheWholeStuff(size, stride, origin, objects, ignoredObjects):
#     if takeScreenshot(size) == False:
#         print("takeScreenshot failed")
#         return False
#     if takeDepth(size, stride, origin, objects, ignoredObjects) == False:
#         print("takeDepth failed")
#         return False
#     if takeMask(size, stride, origin, objects, ignoredObjects) == False:
#         print("takeMask failed")
#         return False
#     return True


# # You must give an unreal object as parameter (an Actor for instance)
# # The UnrealEnginePython documentation says that all_object() is a
# # heavy method to use. Therefore you should not spam it
# def getCamera(uobject):
#     for o in uobject.all_objects():
#         if (o.get_full_name()[:11] == "CameraActor"):
#             print("Camera name: " + o.get_full_name())
#             return o
