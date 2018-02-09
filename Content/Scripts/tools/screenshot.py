# coding: utf-8

"""Provides the Screenshot class to manage screen captures"""

import os
import time
import numpy as np
from PIL import Image

import unreal_engine as ue
from unreal_engine.classes import ScreenCapture
from unreal_engine.structs import Vector2D, DepthAndMask
from unreal_engine import FColor, FVector


def _tuple2vector2d(t):
    v = Vector2D()
    v.X = t[0]
    v.Y = t[1]
    return v


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
    size : 3-tuple of int
        Screen resolution in pixels per number of images as (nimages,
        width, height).
    camera: actor
        The camera actor from which to take screenshots
    ignored_actors: list of actors, optional
        A list of actors to ignore when capturing depth and mask

    """
    def __init__(self, output_dir, size, camera, ignored_actors=[]):
        self.output_dir = output_dir
        self.camera = camera
        self.ignored_actors = ignored_actors

        # the size is (width, height)
        self.size = (size[1], size[2])
        self.nimages = size[0]

        # preallocate the captured images
        self.images = {
            'scene': np.zeros((size[0], size[1], size[2], 4), dtype=np.uint8),
            'depth': np.zeros(size, dtype=np.float16),
            'masks': np.zeros(size, dtype='U64')  # max 64 chars in actor names
        }
        self._index = 0
        self._capture_time = 0

    def capture(self):
        """Take screenshots and push them to memory"""
        t1 = time.time()

        # scene screenshot
        img = ScreenCapture.CaptureScene()

        if self._is_valid_image(img):
            # we have FColor RGBA pixels
            array = np.asarray(img).reshape(self.size[0], self.size[1], 4)
            self.images['scene'][self._index][:] = array

        # depth and masks screenshots
        img = ScreenCapture.CaptureDepthAndMask(
            self.camera, _tuple2vector2d(self.size), self.ignored_actors)

        if self._is_valid_image(img):
            # extract masks
            array = np.asarray([p.Mask for p in img]).reshape(self.size)
            self.images['masks'][self._index][:] = array

            # extract depth
            array = np.asarray([p.Depth for p in img]).reshape(self.size)
            self.images['depth'][self._index][:] = array

        self._index +=1
        self._capture_time += time.time() - t1

    def save(self):
        """Save the captured images in the output directory"""
        ue.log('saving {} screenshots to {}...'.format(
            sum(len(v) for v in self.images.values()), self.output_dir))

        # create the subdirectory 'scene', 'depth' or 'masks'
        for name in ('scene', 'depth', 'masks'):
            path = os.path.join(self.output_dir, name)
            if not os.path.isdir(path):
                os.makedirs(path)

        t1 = time.time()
        self._save_scenes()
        t2 = time.time()
        masks = self._save_masks()
        t3 = time.time()
        max_depth = self._save_depth()
        t4 = time.time()

        ue.log('capture time: {}s'.format(self._capture_time))
        ue.log('saving time: scenes={}s, mask={}s, depth={}s'.format(t2-t1, t3-t2, t4-t3))
        return {'masks': masks, 'max_depth': max_depth}

    def _is_valid_image(self, image):
        """Return True if the `image` has the expected size, False otherwise"""
        if not len(image):
            ue.log_error("screenshot: empty image detected")
            return False

        expected_size = self.size[0] * self.size[1]
        if len(image) != expected_size:
            ue.log_error("screenshot: bad image size {} (must be {})"
                         .format(len(image), expected_size))
            return False

        return True

    def _get_filename(self, name, index):
        """Return the filename `output_dir`/`name`/`name`_`index`.png"""
        # filename index is padded with zeros: 1 -> '001'
        n = '0' * (len(str(self.nimages)) - len(str(index))) + str(index)
        return os.path.join(self.output_dir, name, '{}_{}.png'.format(name, n))

    def _save_scenes(self):
        images = self.images['scene'][:, :, :, :3]
        for n, image in enumerate(images):
            filename = self._get_filename('scene', n)
            self._write_png(image, filename, 'RGB')

    def _save_masks(self):
        # the masks are actor names, we are mapping a unique color
        # code to each actor (sorted by names, from 0 to 255)
        actors = set(self.images['masks'].flatten())
        actor_code = {'': 0}
        if len(actors) == 0:
            ue.log_warning('no masks, empty scene?')
        else:
            # build the color code
            offset = int(255 / len(actors))
            for n, a in enumerate(sorted(actors)):
                if a:
                    actor_code[a] = (n+1) * offset

        # replace the actor name by its color code
        im = np.zeros(self.size, dtype=np.uint8)
        for n, image in enumerate(self.images['masks']):
            im[:] = np.vectorize(lambda p: actor_code[p])(image)
            filename = self._get_filename('masks', n)
            self._write_png(im, filename, 'L')

        # replace the empty name (ie no hit during the raycast) by Sky
        actor_code['Sky'] = 0
        del actor_code['']

        return actor_code

    def _save_depth(self):
        images = self.images['depth']

        # extract global max depth (on all images)
        max_depth = images.max()
        if max_depth == 0.0:
            ue.log_warning('max depth is 0, empty scene?')
        else:
            # depth images quantification in [0, 1]
            images *= (255 / max_depth)
            for n, image in enumerate(images):
                filename = self._get_filename('depth', n)
                self._write_png(image, filename, 'L')

        return max_depth

    @staticmethod
    def _write_png(image, filename, mode):
        Image.fromarray(image.astype(np.uint8, copy=False), mode).save(filename)
