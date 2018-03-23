import json
import os

import unreal_engine as ue
from unreal_engine.classes import Screenshot


# TODO implement a mode 'json_only' where we don't take captures but
# only the status.

class Saver:
    """Take screen captures during a run and save them at the end

    The saver manages screenshots and scene's status. It store them
    during a run and save them at the end, respectively as png images
    (scene, depth and masks) and status.json file.

    Parameters
    ----------
    size : tuple
        The size of a scene the screen resolution times the number of
        images captured in a single scene, in the form (width, height,
        nimages).
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
        self.dry_mode = dry_mode

        # an empty list to append status along the run
        self.status = []

        self.reset()

    def is_dry_mode(self):
        """Return True if saving is disabled, False otherwise"""
        return self.dry_mode is True

    def reset(self):
        """Reset the saver and delete all data in cache"""
        if not self.is_dry_mode():
            Screenshot.Initialize(
                int(self.size[0]), int(self.size[1]), int(self.size[2]),
                self.origin)

    def ignore_actors(self, actors):
        """Ignore the `actors` when taking screenshots"""
        if not self.is_dry_mode():
            Screenshot.SetIgnoredActors(actors)

    def capture(self, scene):
        if not self.is_dry_mode():
            Screenshot.Capture(scene.get_ignored_actors())
            self.status.append(scene.get_status())

    def save(self, output_dir):
        if self.is_dry_mode():
            return True

        ue.log(f'saving capture to {output_dir}')

        # save the captured images as PNG
        done, max_depth, masks = Screenshot.Save(output_dir)
        if not done:
            ue.log_warning(f'failed to save images to {output_dir}')
            return False

        # save the status as JSON file
        self.status.append({'max_depth': max_depth, 'masks': masks})
        json_file = os.path.join(output_dir, 'status.json')
        open(json_file, 'w').write(json.dumps(self.status, indent=4))

        return True
