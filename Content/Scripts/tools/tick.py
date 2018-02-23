class Tick:
    """Tick at a requested frequency within the main game loop

    This ticker responds each `tick_interval` ticks of the game's main
    loop and return the tick count since it started ticking.

    """
    def __init__(self, tick_interval=2):
        # Interval between two ticks
        self.tick_interval = tick_interval

        # True when the ticker is active
        self.is_ticking = False

        # Count the ticks at the given interval
        self.counter = 0

        # two variables to compute the ticks interval
        self._t_tick, self._t_last_tick = 0, 0

    def tick(self, dt):
        """Return the tick count if ticking at the requested interval

        Return -1 if not ticking or ticking out of interval.

        `dt` is not used here and is the time since the last tick.

        """
        if not self.is_ticking:
            return -1

        self._t_tick += 1
        if self._t_tick - self._t_last_tick >= self.tick_interval:
            self._t_last_tick = self._t_tick
            self.counter += 1
            return self.counter
        else:
            return -1
