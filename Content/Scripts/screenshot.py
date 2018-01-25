"""Take screenshots of raw scene, depth field and object masks"""

import os
import png

import unreal_engine as ue
from unreal_engine.classes import testScreenshot
from unreal_engine.structs import IntSize
from unreal_engine import FColor, FVector


class Screenshot:
    def __init__(self, res_x, res_y, camera, objects, ignored_objects):
        # size of the captured images (in pixels)
        self.size = IntSize()
        self.size.X = res_x
        self.size.Y = res_y

        self.camera = camera
        self.objects = objects
        self.ignored_objects = ignored_objects

        # store the images
        self.images = {'scene': [], 'depth': [], 'masks': []}

    def capture(self):
        """Takes scene, masks and depth screenshots of the scene"""
        self._capture_location()
        # self.images['scene'].append(self._capture_scene())
        # self.images['depth'].append(self._capture_depth())
        # self.images['masks'].append(self._capture_masks())

    # def just_a_ray(self):
    #     world = self.camera.get_world()
    #     location_from = FVector(0, 0, 100),
    #     location_to = FVector(0, 0, -100)
    #     # collision_query = FCollisionQueryParams('clickableTrace', False)
    #     world.call_function(
    #         'LineTraceSingleByChannel',
    #         location_from, location_to,
    #         ECollisionChannel.ECC_Visibility)# ,
    #         # collision_query)

        # testScreenshot.JustARay(
        #     self.camera.get_world(),
        #     FVector(0, 0, 100), FVector(0, 0, -100))

    def save(self, path):
        """Save the captured images as PNG in `path`"""
        ue.log('saving {} screenshots to {}...'.format(
            sum(len(v) for v in self.images.values()), path))

        for k, v in self.images.items():
            self._save_images(
                v, k, path, 'RGB' if k == 'scene' else 'grayscale')

    def _save_images(self, images, name, path, format):
        if not images:
            ue.log('no {} image to save'.format(name))
            return

        # write images in the 'scene', 'depth' or 'masks' subdirectory
        path = os.path.join(path, name)
        if not os.path.isdir(path):
            os.makedirs(path)

        nimages = len(str(len(images)))
        for n, image in enumerate(images):
            # 1 -> '001'
            n = '0' * (nimages - len(str(n))) + str(n)

            self._save_png(image, os.path.join(
                path, '{}_{}.png'.format(name, n)), format)

    def _valid_image(self, image, format):
        """Return True if the image has the expected size

        The image `format` must be 'RGB' or 'grayscale'.

        """
        if len(image) == 0:
            ue.log_error("screenshot: empty image")
            return []

        expected_size = self.size.X * self.size.Y
        if format == 'RGB':
            expected_size *= 3

        if len(image) != expected_size:
            ue.log_error(
                "screenshot: bad image size {} (must be {})"
                .format(len(image), expected_size))
            return []

        return image

    def _capture_location(self):
        image = []
        image = testScreenshot.CaptureHitLocation(self.size, 1, self.camera)
        ue.log('pixel 0: {}'.format(image[0]))
        return []

    def _capture_scene(self):
        image = []
        image = testScreenshot.CaptureScreenshot(self.size)
        return self._valid_image(image, 'RGB')

    def _capture_depth(self):
        image = []
        image = testScreenshot.CaptureDepth(
            self.size, 1, self.camera, self.objects, self.ignored_objects)
        return self._valid_image(image, 'grayscale')

    def _get_pixel(self, image, x, y, mode):
        """Return the pixel (x, y) from the image"""
        if mode == 'RGB':
            idx = 3 * (y * self.size.X + x)
            try:
                return [image[idx], image[idx+1], image[idx+2]]
            except IndexError:
                return [0, 0, 0]
        elif mode == 'grayscale':
            try:
                return image[y * self.size.X + x]
            except IndexError:
                return 0
        else:
            ue.log_error(
                'unknown mode {}, must be RGB or grayscale'.format(mode))

    def _save_png(self, image, filename, format):
        """Save the `image` as a PNG file to `filename`

        The `format` must be 'RGB' or 'grayscale'

        """
        array = [[self._get_pixel(image, x, y, format)
                  for x in range(self.size.X)]
                 for y in range(self.size.Y)]

        if format == 'grayscale':
            format = 'L'  # grayscale code for png
        png.from_array(array, format).save(filename)



# # pixel_array is an array of integers. Every group of 3 values is a
# # pixel with R, G and B value flag argument is an integer used to
# # build the filename to know if it is a screenshot (1), a depth (2) or
# # a mask (3)
# def savePNG(pixel_array, size, flag):
#     if (len(pixel_array) == 0):
#         print("savePNG failed. The array of pixel is empty")
#         return False
#     if (len(pixel_array) != size.X * size.Y * 3):
#         print("savePNG failed. The length of the array of pixel is wrong")
#         return False

#     png_pixels = []
#     for y in range(0, size.Y):
#         line = []
#         for x in range(0, width):
#             pixel = pixel_array[y * width + x]
#             line.append([pixel.r, pixel.g, pixel.b])

#         png_pixels.append(line)

#     path = os.environ['MYPROJECT'] + "/Test_pictures/"
#     if os.path.isdir(path) == False:
#         os.makedirs(path)
#         print("--> 'Test_pictures' directory created")

#     pic_name = testScreenshot.BuildFileName(flag)
#     png.from_array(png_pixels, 'RGB').save(path + pic_name)
#     #print("--> picture '" + pic_name + "' saved in " + path)
#     return True

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
