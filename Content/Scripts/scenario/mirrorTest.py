import json
import os
import unreal_engine as ue
from scenario.test import Test
from shutil import copyfile


class MirrorTest(Test):
    def play_run(self):
        if self.run == 2:
            return
        super().play_run()
        # ue.log("Run {}/{}: Possible run".format(self.run + 1,
        #       4 if self.saver.is_dry_mode is False else 2))

    def stop_run(self, scene_index, total):
        if self.run == 1 and self.set_magic_tick() is False:
            self.del_actors()
            return False
        if self.run == 0:
            self.reset_actors()
        else:
            self.del_actors()
        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index, total))
            # reset actors if it is the last run
            self.saver.reset(True if self.run == 1 else False)
        self.run += 1
        if self.run == 2 and self.saver.is_dry_mode is False:
            self.generate_magic_runs(scene_index, total)
        return True

    def capture(self):
        super().capture()
        self.fill_check_array()

    def generate_magic_runs(self, scene_index, total):
        if '2' not in self.movement:
            magic_tick = self.params['magic']['tick'] + 2
            magic_tick2 = 100
            # ue.log("magic tick = {}".format(magic_tick))
        else:
            magic_tick = self.params['magic']['tick'][0] + 2
            magic_tick2 = self.params['magic']['tick'][1] + 2
            # ue.log("magic ticks = {} and {}".format(magic_tick, magic_tick2))
        # next line is removing the run subdirectory from the path
        subdir = self.get_scene_subdir(scene_index, total)[:-2]
        pic_types = ["scene", "depth", "masks"]
        # ue.log('Run 3/4: Impossible run')
        for pic_type in pic_types:
            if not os.path.exists("{}/3/{}".format(subdir, pic_type)):
                os.makedirs("{}/3/{}".format(subdir, pic_type))
            for i in range(1, magic_tick + 1):
                dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                copyfile(src, dst)
            for i in range(magic_tick, magic_tick2 + 1):
                dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                copyfile(src, dst)
            if '2' in self.movement:
                for i in range(magic_tick2, 101):
                    dst = "{}/3/{}/{}_{}.png".format(subdir, pic_type,
                                                     pic_type, str(i).zfill(3))
                    src = "{}/1/{}/{}_{}.png".format(subdir, pic_type,
                                                     pic_type, str(i).zfill(3))
                    copyfile(src, dst)
        # ue.log('saved captures to {}/{}'.format(subdir, 3))
        # ue.log('Run 4/4: Impossible run')
        for pic_type in pic_types:
            if not os.path.exists("{}/4/{}".format(subdir, pic_type)):
                os.makedirs("{}/4/{}".format(subdir, pic_type))
            for i in range(1, magic_tick + 1):
                dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                src = "{}/2/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                copyfile(src, dst)
            for i in range(magic_tick, magic_tick2 + 1):
                dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                src = "{}/1/{}/{}_{}.png".format(subdir, pic_type, pic_type,
                                                 str(i).zfill(3))
                copyfile(src, dst)
            if '2' in self.movement:
                for i in range(magic_tick2, 101):
                    dst = "{}/4/{}/{}_{}.png".format(subdir, pic_type,
                                                     pic_type, str(i).zfill(3))
                    src = "{}/2/{}/{}_{}.png".format(subdir, pic_type,
                                                     pic_type, str(i).zfill(3))
                    copyfile(src, dst)
        # ue.log('saved captures to {}/{}'.format(subdir, 4))
        self.generate_magic_status(subdir, [magic_tick, magic_tick2])
        # ue.log("generated json files")

    def generate_magic_status(self, subdir, slice_index):
        # build the status.json, slice_index are magic_tick as a list
        json_1 = json.load(open('{}/1/status.json'.format(subdir), 'r'))
        json_2 = json.load(open('{}/2/status.json'.format(subdir), 'r'))

        # the headers must be the same (excepted the actor names but do
        # not impact the end user) TODO for now (as of commit e5e2c25) the
        # 'masks' entry is different in runs 1 and 2 TODO to have same
        # names, maybe change the runs implementation: spawn actors only
        # at scene init, and destroy them at scene end but not between 2
        # runs.
        json_3 = {'header': json_1['header']}
        json_4 = {'header': json_1['header']}
        json_3['header']['is_possible'] = False
        json_4['header']['is_possible'] = False

        # update the frames according to the slice index
        f1, f2 = json_1['frames'], json_2['frames']
        if len(slice_index) == 2:  # dynamic_2 case
            idx1, idx2 = slice_index[0], slice_index[1]
            json_3['frames'] = f1[:idx1] + f2[idx1:idx2] + f1[idx2:]
            json_4['frames'] = f2[:idx1] + f1[idx1:idx2] + f2[idx2:]
        else:  # dynamic_1 or static cases
            idx = slice_index[0]
            json_3['frames'] = f1[:idx] + f2[idx:]
            json_4['frames'] = f2[:idx] + f1[idx:]

        # make sure the dest directories exist
        for i in (3, 4):
            d = '{}/{}'.format(subdir, i)
            if not os.path.isdir(d):
                os.makedirs(d)

        # save the status as JSON files
        with open('{}/3/status.json'.format(subdir), 'w') as fin:
            fin.write(json.dumps(json_3, indent=4))
        with open('{}/4/status.json'.format(subdir), 'w') as fin:
            fin.write(json.dumps(json_4, indent=4))

        # print('\n'.join('{} {}'.format(
        #     f3[magic_object]['material'], f4[magic_object]['material'])
        #     for f3, f4 in zip(json_3['frames'], json_4['frames'])))

    def is_over(self):
        return True if self.run == 2 else False

    def set_magic_tick(self):
        if super().set_magic_tick() is False:
            return False
        magic_tick = self.params['magic']['tick']
        # checking the location and rotation of each actor
        # during the magic frame(s)
        if isinstance(self.params['magic']['tick'], int):
            for actor in \
                    range(len(self.check_array['location'][0][magic_tick])):
                if self.compare_location_in_frame(actor, magic_tick) is False:
                    ue.log_warning("An actor location doesn't match" +
                                   " in each possible run")
                    return False
        elif isinstance(self.params['magic']['tick'], list):
            for actor in \
                    range(len(self.check_array['location'][0][magic_tick[0]])):
                if (self.compare_location_in_frame(actor, magic_tick[0])
                        is False or
                        self.compare_location_in_frame(actor, magic_tick[1])
                        is False):
                    ue.log_warning("An actor location doesn't match" +
                                   " in each possible run")
                    return False
        """
        # checking the location and rotation of each actor (except magic one)
        # in the first and last frame of each run
        for actor in \
                range(len(self.check_array['location'][0][0])):
            if actor == self.params['magic']['actor']:
                continue
            if (self.compare_location_in_frame(actor, 0) is False or
                    self.compare_location_in_frame(actor, 99) is False):
                ue.log_warning("An actor location doesn't match" +
                               " in each possible run")
                for j in range(100):
                    ue.log_warning("{}: {} vs {}, {} vs {}, {} vs {} | {} vs {}, {} vs {}, {} vs {}"
                                   .format(j, self.check_array['location'][0][j][actor][0].x,
                                           self.check_array['location'][1][j][actor][0].x,
                                           self.check_array['location'][0][j][actor][0].y,
                                           self.check_array['location'][1][j][actor][0].y,
                                           self.check_array['location'][0][j][actor][0].z,
                                           self.check_array['location'][1][j][actor][0].z,
                                           self.check_array['location'][0][j][actor][1].yaw,
                                           self.check_array['location'][1][j][actor][1].yaw,
                                           self.check_array['location'][0][j][actor][1].roll,
                                           self.check_array['location'][1][j][actor][1].roll,
                                           self.check_array['location'][0][j][actor][1].pitch,
                                           self.check_array['location'][1][j][actor][1].pitch))
                return False
        """

    def compare_location_in_frame(self, actor, frame):
        return (
            self.check_array['location'][0][frame][actor][0].x ==
            self.check_array['location'][1][frame][actor][0].x and
            self.check_array['location'][0][frame][actor][0].y ==
            self.check_array['location'][1][frame][actor][0].y and
            self.check_array['location'][0][frame][actor][0].z ==
            self.check_array['location'][1][frame][actor][0].z and
            self.check_array['location'][0][frame][actor][1].yaw ==
            self.check_array['location'][1][frame][actor][1].yaw and
            self.check_array['location'][0][frame][actor][1].roll ==
            self.check_array['location'][1][frame][actor][1].roll and
            self.check_array['location'][0][frame][actor][1].pitch ==
            self.check_array['location'][1][frame][actor][1].pitch)
