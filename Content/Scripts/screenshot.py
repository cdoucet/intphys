import unreal_engine as ue
import os
import png
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize
from unreal_engine import FColor

# pixel_array is an array of integers. Every group of 3 values is a pixel with R, G and B value
# flag argument is an integer used to build the filename to know if it is a screenshot (1), a depth (2) or a mask (3)
def savePNG(pixel_array, size, flag):
    if (len(pixel_array) == 0):
        print "savePNG failed. The array of pixel is empty"
        return False
    if (len(pixel_array) != size.X * size.Y * 3):
        print "savePNG failed. The length of the array of pixel is wrong"
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

def takeDepth(size, stride, origin, objects, ignoredObjects):
    print "--> beginning of the depth script"
    pixel_array = []
    pixel_array = testScreenshot.CaptureDepth(size, stride, origin, objects, ignoredObjects)
    if (len(pixel_array) == 0):
        print "takeDepth failed. The array of pixels is empty"
        return False
    savePNG(pixel_array, size, 2)
    print "--> end of the depth script"
    return True

def takeMask(size, stride, origin, objects, ignoredObjects):
    print "--> beginning of the mask script"
    pixel_array = []
    pixel_array = testScreenshot.CaptureMask(size, stride, origin, objects, ignoredObjects)
    if (len(pixel_array) == 0):
        print "takeMask failed. The array of pixels is empty"
        return False
    savePNG(pixel_array, size, 3)
    print "--> end of the mask script"
    return True

def takeScreenshot(size):
    print "--> beginning of the screenshot script"
    print "size = X->", size.X, " Y->", size.Y
    pixel_array = []
    pixel_array = testScreenshot.CaptureScreenshot(size, pixel_array)
    if (len(pixel_array) == 0):
        print "takeScreenshot failed. The array of pixels is empty"
        return False
    savePNG(pixel_array, size, 1)
    print "--> end of the screenshot script"
    return True

def doTheWholeStuff(size, stride, origin, objects, ignoredObjects):
    if takeScreenshot(size) == False:
        print "takeScreenshot failed"
        return False
    if takeDepth(size, stride, origin, objects, ignoredObjects) == False:
        print "takeDepth failed"
        return False
    if takeMask(size, stride, origin, objects, ignoredObjects) == False:
        print "takeMask failed"
        return False
    return True

def salut(self):
    print "salut!"
