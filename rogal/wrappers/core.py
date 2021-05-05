import collections

from ..console import Console, RootPanel


class IOWrapper:

    def __init__(self,
        console_size,
        palette,
    ):
        self.console_size = console_size
        self._palette = palette
        self._events_queue = collections.deque()

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

    def create_console(self, size=None):
        # if not size:
        #     return None
        size = size or self.console_size
        return Console(size)

    def create_panel(self, size=None):
        console = self.create_console(size)
        return RootPanel(console, self.palette)

    def flush(self, console):
        """Show contents of given console on screen."""
        raise NotImplementedError()

    def process_events(self, events):
        """Process events - update, filter, merge, etc."""
        return events

    def get_events_gen(self, wait=None):
        """Get all pending events."""
        yield from ()

    def events_gen(self, wait=None):
        """Yield events."""
        while self._events_queue:
            yield self._events_queue.popleft()

        events_gen = self.get_events_gen(wait)
        processed_events = self.process_events(events_gen)
        self._events_queue.extend(processed_events)

        while self._events_queue:
            yield self._events_queue.popleft()

    def __enter__(self):
        self.initialize()
        return self

    def close(self):
        """Close and clean up all resources before exiting."""
        return

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class MockWrapper(IOWrapper):

    def flush(self, console):
        if isinstance(console, RootPanel):
            console = console.console
        from . import ansi
        ansi.show_console(console)

