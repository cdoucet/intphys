import unreal_engine as ue
from scenario.test import Test


class FullTest(Test):
    def play_run(self):
        if self.run == 4:
            return
        # ue.log("Run {}/4: Possible run".format(self.run + 1))
        super().play_run()

    def stop_run(self, scene_index, total):
        self.ticker = 0
        if self.run == 1 and self.set_magic_tick() is False:
            self.del_actors()
            return False
        if self.run != 3:
            self.reset_actors()
        else:
            self.del_actors()
        if not self.saver.is_dry_mode:
            self.saver.save(self.get_scene_subdir(scene_index, total))
            # reset actors if it is the last run
            self.saver.reset(True if self.run == 3 else False)
        self.run += 1
        return True

    def tick(self):
        super().tick()
        if self.run <= 1:
            self.fill_check_array()
        elif isinstance(self.params['magic']['tick'], int) and \
                self.ticker == self.params['magic']['tick']:
            self.play_magic_trick()
        elif not isinstance(self.params['magic']['tick'], int) and \
                self.ticker in self.params['magic']['tick']:
            self.play_magic_trick()

    def is_over(self):
        return True if self.run == 4 else False
