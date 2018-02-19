"""This module handles game loop ticks.

 It provides 3 ticking levels at which some functions can be
 registered:
   * the 'fast' level ticks at each game tick,
   * the 'slow' level ticks each few game loop as defined by
     tick_interval,
   * the 'final' level ticks only once, at the very end of the scene
     rendering.

A function f is registered to tick at a given level l using the
function tick.add_hook(f, l), l being 'slow', 'fast' or 'final'.

The 'slow' level is used for taking screenshots, the 'fast' one for
scene animation.

"""

import unreal_engine as ue

class Tick:
    def __init__(self, nticks=100, tick_interval=2, ticks_rate=1.0/8.0):
        # Number of ticks to execute before calling the final hooks
        self.nticks = nticks

        # Interval between two game ticks in which the slow hooks are called
        self.tick_interval = tick_interval

        # Tables registering hooks for the different ticking levels
        self.hooks = {'slow': [], 'fast': [], 'final': []}

        # two variables to compute the ticks interval
        self._t_tick, self._t_last_tick = 0, 0

        # A tick counter, from 0 to nticks
        self._ticks_counter = 0

        # True when the game is ticking
        self._is_ticking = False

    def reset(self):
        """Reset the ticker to it's initial state"""
        self._t_tick, self._t_last_tick = 0, 0
        self._ticks_counter = 0

    def run(self):
        """Run the game and execute the tick hooks"""
        self._is_ticking = True

    def set_ticks_remaining(self, ticks_remaining):
        """Set the number of slow ticks before the end of the scene"""
        self.nticks = ticks_remaining

    def get_ticks_remaining(self):
        """Return the number of ticks remaining before the end of the scene"""
        return self.nticks - self.ticks_counter

    def get_counter(self):
        """Return the number of slow ticks since the beginning of the scene"""
        return self._ticks_counter

    def add_hook(self, func, level):
        """Register a hook function `func` called at a given ticking `level`

        The function `func` should take a single argument and return nil.
        The level must be 'slow', 'fast', or 'final'.

        """
        self.hooks[level].append(func)

    def clear_hooks(self):
        """Clear all the registered hooks"""
        for level in self.hooks.keys():
            self.hooks[level] = []

    def run_hooks(self, level):
        """Run all the registerd at a given ticking level"""
        for hook in self.hooks[level]:
            try:
                hook()
            except Exception as err:
                ue.log('error in tick {}, hook {}: {}'
                       .format(self.get_counter(), hook.__name__, err))

    def tick(self, dt):
        """This function must be called at each game loop by the engine

        It increment the tick counter, calling each registered hook
        until the end of the scene.

        """
        # dt not used here is the time since the last tick
        if self._is_ticking and self._ticks_counter < self.nticks:
            self.run_hooks('fast')

            if self._t_tick - self._t_last_tick >= self.tick_interval:
                self._t_last_tick = self._t_tick
                self._ticks_counter += 1
                self.run_hooks('slow')

            self._t_tick += 1
        elif self._is_ticking:
            self.run_hooks('final')
            self.reset()
