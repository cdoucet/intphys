import json
import os

import unreal_engine as ue
from unreal_engine.classes import ScreenshotManager


class Saver:
    """Take screen captures during a run and save them at the end

    The saver manages screenshots and scene's status. It store them
    during a run and save them at the end, respectively as png images
    (scene, depth and masks) and status.json file.

    Parameters
    ----------
    size : tuple of (width, height, nimages)
        The size of a scene where (width, height) is the screen
        resolution in pixels and nimages the number of images captured
        in a single scene.
    origin : AActor
        The actor from which to capture screenshots (usually the
        camera).
    dry_mode : bool, optional
        When False (default), capture PNG images and metadata from the
        rendered scenes. When True, do not take any captures nor save
        any data.

    """
    def __init__(self, size, origin, dry_mode=False):
        self.size = size
        self.origin = origin
        self.is_dry_mode = dry_mode

        # an empty list to append status along the run
        self.status = []

        # initialize the capture. TODO We initialize the manager even
        # if if we are in dry mode because we may use it in check runs
        ScreenshotManager.Initialize(
            int(self.size[0]), int(self.size[1]), int(self.size[2]),
            self.origin, True)

    def capture(self, scene):
        """Push the scene's current screenshot and status to memory"""
        if not self.is_dry_mode:
            # scene, depth and masks images are stored from C++
            ScreenshotManager.Capture(scene.get_ignored_actors())
            self.status.append(scene.get_status())

    def reset(self):
        """Reset the saver and delete all data in cache"""
        if not self.is_dry_mode:
            ScreenshotManager.Reset()
            self.status = []

    def save(self, output_dir):
        """Save the captured data to `output_dir`"""
        if self.is_dry_mode:
            return True

        ue.log(f'saving capture to {output_dir}')

        # save the captured images as PNG
        # TODO postprocess masks of walls (merge)
        done, max_depth, masks = ScreenshotManager.Save(output_dir)
        if not done:
            ue.log_warning(f'failed to save images to {output_dir}')
            return False

        # save the status as JSON file
        self.status.append({'max_depth': max_depth, 'masks': masks})
        json_file = os.path.join(output_dir, 'status.json')
        open(json_file, 'w').write(json.dumps(self.status, indent=4))

        return True
