import unreal_engine as ue
import os
import png
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize
from unreal_engine import FColor

def savePNG(pixel_array, size, flag):
    png_pixels = []
    height = size.Y
    width = size.X
    for y in range(0, height):
        line = []
        for x in range(0, width):
            index = y * width + x
            print("index = ", pixel_array[index])
            pixel = pixel_array[index]
            line.append([pixel.r, pixel.g, pixel.b])
        png_pixels.append(line)
    path = os.environ['MYPROJECT'] + "/Test_pictures/"
    if os.path.isdir(path) == False:
        os.makedirs(path)
        print("--> 'Test_pictures' directory created")
    pic_name = testScreenshot.BuildFileName(flag)
    png.from_array(png_pixels, 'RGB').save(path + pic_name)
    print("--> picture " + pic_name + " saved in " + path)

def takeScreenshot(size):
    width, height = ue.get_viewport_size()
    size.X = width
    size.Y = height
    print("size = X->", width , " Y->", height)
    print("--> beginning of the screenshot script")
    testScreenshot.salut() # it is important to be gentle with the user
    pixel_array = []
    pixel_array = testScreenshot.CaptureScreenshot(size, pixel_array)
    savePNG(pixel_array, size, 1)
    print("--> end of the screenshot script")
    return res

def doTheWholeStuff(size, stride, origin, objects, ignoredObjects):
    takeScreenshot(size)

def salut():
    print("salut depuis {}".format(__file__))
