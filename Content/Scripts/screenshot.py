import unreal_engine as ue
import os
import png

# run play in the editor and execute this script (with ue.exec) from the python console

# check if a viewport is active
def check():
    if ue.get_viewport_size() == None:
        raise ValueError("--> No viewport active")
        return -1
    if os.environ['MYPROJECT'] == None:
        raise ValueError("--> MYPROJECT environment variable not set")
        return -1
    return 0

# draw the picture from every pixels
def draw_from_pixels(width, height, pixels):
    png_pixels = []
    for y in range(0, height):
        line = []
        for x in range(0, width):
            index = y * width + x
            pixel = pixels[index]
            line.append([pixel.r, pixel.g, pixel.b])
        png_pixels.append(line)
    return png_pixels

# save the png to a directory named "Test_pictures" in the project directory
# (in the "MYPROJECT" environment variable).
# Create the directory if not found.
def save_picture(png_pixels):
    path = os.environ['MYPROJECT'] + "/Test_pictures/"
    if os.path.isdir(path) == False:
        os.makedirs(path)
        print "--> 'Test_pictures' file created"
    pic_name = "pic.png"
    png.from_array(png_pixels, 'RGB').save(path + pic_name)
    print "--> picture saved in " + path

# first function to call (return -1 if fail, 0 otherwise)
def __init__():
    print "--> beginning of the screenshot script"
    if (check() == -1):
        return -1
    width, height = ue.get_viewport_size()
    pixels = ue.get_viewport_screenshot()
    png_pixels = draw_from_pixels(width, height, pixels)
    save_picture(png_pixels)
    print "--> end of the screenshot script"
    return 0

# script that call the first function and throw if an error kick in
try:
    __init__()
except ValueError, e:
    print str(e)
