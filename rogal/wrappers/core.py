import collections

from ..console import RootPanel


class InputWrapper:

    def __init__(self):
        self._events_queue = collections.deque()

    def process_events_gen(self, events_gen):
        """Process events - update, filter, merge, etc."""
        yield from events_gen

    def get_events_gen(self, timeout=None):
        """Get all pending events."""
        yield from ()

    def events_gen(self, timeout=None):
        """Yield events."""
        while self._events_queue:
            yield self._events_queue.popleft()

        events_gen = self.get_events_gen(timeout)
        processed_events_gen = self.process_events_gen(events_gen)
        self._events_queue.extend(processed_events_gen)

        while self._events_queue:
            yield self._events_queue.popleft()


class IOWrapper:

    CONSOLE_CLS = None
    ROOT_PANEL_CLS = RootPanel

    def __init__(self,
        console_size,
        palette,
        title=None,
        *args, **kwargs,
    ):
        self.title = title
        self.console_size = console_size
        self._palette = palette
        self._input = None

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, palette):
        # TODO: Some event on palette change forcing everything to redraw?
        self._palette = palette

    @property
    def is_initialized(self):
        return False

    def initialize(self):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()

    def create_console(self, size=None):
        size = size or self.console_size
        return self.CONSOLE_CLS(size)

    def create_panel(self, size=None):
        console = self.create_console(size)
        return self.ROOT_PANEL_CLS(console, self.palette)

    def flush(self, panel):
        """Show contents of given console on screen."""
        raise NotImplementedError()

    def events_gen(self, wait=None):
        """Yield events."""
        if not self.is_initialized:
            self.initialize()
        yield from self._input.events_gen(wait)

    def __enter__(self):
        self.initialize()
        return self

    def close(self):
        """Close and clean up all resources before exiting."""
        if self.is_initialized:
            self.terminate()

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

