class Tick:
    """Tick at a requested frequency within the main game loop

    This ticker responds each `tick_interval` ticks of the game's main
    loop and return the tick count since it started ticking.

    """
    def __init__(self, tick_interval=2):
        # Interval between two ticks
        self._tick_interval = tick_interval

        # True when the ticker is active
        self._is_ticking = False

        # True when ticking at the requested interval
        self._on_tick = False

        # Count the ticks at the requested interval
        self._counter = 0

        # two variables to compute the intervals
        self._t_tick, self._t_last_tick = 0, 0

    def on_tick(self):
        """True when ticking, False otherwise"""
        return self._is_ticking and self._on_tick

    def start(self):
        """Start ticking"""
        self._is_ticking = True

    def stop(self):
        """Stop ticking but don't reset the ticks counter"""
        self._is_ticking = False

    def reset(self):
        """Reset the ticks counter"""
        self._counter = 0
        self._t_tick = 0
        self._t_last_tick = 0

    def get_count(self):
        """Return the number of ticks since the last reset"""
        return self._counter

    def tick(self, dt):
        if self._is_ticking and self._update(dt):
            self._counter += 1
            self._on_tick = True
        else:
            self._on_tick = False

    def _update(self, dt):
        """Update the ticker, return True on tick, False otherwise

        `dt` is not used here and is the time since the last tick.

        """
        self._t_tick += 1

        if self._t_tick - self._t_last_tick >= self._tick_interval:
            self._t_last_tick = self._t_tick
            return True

        return False
