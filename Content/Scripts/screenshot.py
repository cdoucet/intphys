"""Provides the Screenshot class to manage screen captures"""

import os
import png

import unreal_engine as ue
from unreal_engine.classes import ScreenCapture
from unreal_engine.structs import Vector2D, DepthAndMask
from unreal_engine import FColor, FVector


class Screenshot:
    """Capture screenshots of a scene and save them to disk.

    This class exposes two methods:

    * capture() is called during game ticks and takes screenshots and
      push them in memory,

    * save() is called on final tick. It does post-processing and
      saves the captured images to disk.

    Parameters
    ----------
    output_dir : str
        The directory where to write the captured PNG images. Write
        'depth', 'mask' and 'depth' subdirectories in it, or overwrite
        them if existing. The created images are numbered and in PNG
        format, e.g. `output_dir`/depth/depth_012.png.

    res_x, res_y : int
        Screen resolution in pixels

    camera: actor
        The camera actor from which to take screenshots

    ignored_objects: list of actors, optional
        A list of actors to ignore when capturing depth and mask

    """
    def __init__(self, output_dir, res_x, res_y, camera, ignored_objects=[]):
        self.output_dir = output_dir
        self.camera = camera
        self.ignored_objects = ignored_objects

        # size of the captured images (in pixels)
        self.size = Vector2D()
        self.size.X = res_x
        self.size.Y = res_y

        # store the captured images
        self.images = {'scene': [], 'depth': [], 'masks': []}

    def capture(self):
        """Takes scene, masks and depth screenshots of the scene"""
        img_scene = []
        img_scene = ScreenCapture.CaptureScene()
        self.images['scene'].append(self._valid_image(img_scene))

        img_depth_mask = []
        img_depth_mask = ScreenCapture.CaptureDepthAndMask(
            self.camera, self.size, self.ignored_objects)

        self.images['depth'].append(
            self._valid_image([p.Depth for p in img_depth_mask]))

        self.images['masks'].append(
            self._valid_image([p.Mask for p in img_depth_mask]))

    def save(self):
        """Save the captured images in the output directory"""
        ue.log('saving {} screenshots to {}...'.format(
            sum(len(v) for v in self.images.values()), self.output_dir))

        self._save_images(self.images['scene'], 'scene', self.output_dir, 'RGB')
        masks = self._save_masks(self.output_dir)
        max_depth = self._save_depth(self.output_dir)

        return {'masks': masks, 'max_depth': max_depth}

    def _valid_image(self, image):
        """Return the image if it has the expected size, elsewise return []"""
        if len(image) == 0:
            ue.log_error("screenshot: empty image")
            return []

        expected_size = int(self.size.X * self.size.Y)
        if len(image) != expected_size:
            ue.log_error(
                "screenshot: bad image size {} (must be {})"
                .format(len(image), expected_size))
            return []

        return image

    def _save_masks(self, path):
        masks = self.images['masks']
        actors = {pixel for image in masks for pixel in image}

        if len(actors) == 0:
            ue.log_warning('no masks, empty scene?')
        else:
            # map a unique color code to each actor in the images (sorted
            # by names, from 0 to 255)
            offset = int(255 / len(actors))
            actor_code = {a: int((n+1) * offset) for n, a in enumerate(sorted(actors)) if a}
            actor_code[''] = 0

            # replace the actor name by its color code
            for n, image in enumerate(masks):
                masks[n] = [actor_code[p] for p in image]

            self._save_images(masks, 'masks', path, 'grayscale')

            actor_code['Sky'] = 0
            del actor_code['']
            return actor_code

    def _save_depth(self, path):
        images = self.images['depth']

        # extract global max depth (on all images)
        max_depth = max((max(image) for image in images))
        if max_depth == 0.0:
            ue.log_warning('max depth is 0, empty scene?')

        else:
            # depth images quantification in [0, 255]
            quantifier = 255.0 / max_depth
            for n, image in enumerate(images):
                images[n] = [int(pixel * quantifier) for pixel in image]

        self._save_images(images, 'depth', path, 'grayscale')
        return max_depth

    def _save_images(self, images, name, path, format):
        if not images:
            ue.log_warning('no {} image to save'.format(name))
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

    def _get_pixel(self, image, x, y, mode='grayscale'):
        """Return the pixel (x, y) from the image"""
        pixel = image[int(y * self.size.X + x)]
        if mode == 'RGB':
            return [pixel.r, pixel.g, pixel.b]
        else:
            return pixel

    def _save_png(self, image, filename, format):
        """Save the `image` as a PNG file to `filename`"""
        # convert the raw image to a nested list of rows
        array = [[self._get_pixel(image, x, y, format)
                  for x in range(int(self.size.X))]
                 for y in range(int(self.size.Y))]

        if format == 'grayscale':
            format = 'L'  # grayscale code for png

        # save the image
        png.from_array(array, format).save(filename)
