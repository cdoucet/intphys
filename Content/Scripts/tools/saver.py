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
    camera : AActor
        The camera actor from which to capture screenshots.
    dry_mode : bool, optional
        When False (default), capture PNG images and metadata from the
        rendered scenes. When True, do not take any captures nor save
        any data.

    """
    def __init__(self, size, dry_mode=False, output_dir=None):
        self.size = size
        self.camera = None
        if output_dir is None:
            dry_mode = True
        self.is_dry_mode = dry_mode
        self.output_dir = output_dir

        # an empty list to append status along the run
        self.status_header = {}
        self.status = []

        # initialize the capture.
        verbose = False
        ScreenshotManager.Initialize(
            int(self.size[0]), int(self.size[1]), int(self.size[2]),
            None, verbose)

    def capture(self, ignored_actors, status_header, status):
        """Push the scene's current screenshot and status to memory"""
        if not self.is_dry_mode:
            # save the header only once
            if self.status_header == {}:
                self.status_header = status_header
                self.status_header['camera'] = self.camera.get_status()

            # scene, depth and masks images are stored from C++
            ScreenshotManager.Capture(ignored_actors)

            # save the current status
            self.status.append(status)

    def reset(self):
        """Reset the saver and delete all data in cache"""
        if not self.is_dry_mode:
            ScreenshotManager.Reset()
            self.status_header = {}
            self.status = []

    def save(self, output_dir):
        """Save the captured data to `output_dir`"""
        if self.is_dry_mode:
            return True

        # save the captured images as PNG
        done, max_depth, masks = ScreenshotManager.Save(output_dir)
        if not done:
            ue.log_warning(f'failed to save images to {output_dir}')
            return False

        # save images max depth and actors's masks to status
        self.status_header.update({'max_depth': max_depth, 'masks': masks})
        status = {'header': self.status_header, 'frames': self.status}

        # save the status as JSON file
        json_file = os.path.join(output_dir, 'status.json')
        with open(json_file, 'w') as fin:
            fin.write(json.dumps(status, indent=4))
        ue.log(f'saved captures to {output_dir}')
        return True

    def update_camera(self, camera):
        self.camera = camera
        ScreenshotManager.SetOriginActor(camera.actor)
