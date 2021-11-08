import collections

from ..console import RootPanel


class InputWrapper:

    def __init__(self):
        self._events_queue = collections.deque()
        self.events_processors = []

    def process_events(self, events_gen):
        """Process events - update, filter, merge, etc."""
        for events_processor in self.events_processors:
            events_gen = events_processor(events_gen)
        yield from events_gen

    def get_events_gen(self, timeout=None):
        """Get all pending events."""
        yield from ()

    def events_gen(self, timeout=None):
        """Yield events."""
        while self._events_queue:
            yield self._events_queue.popleft()

        events_gen = self.get_events_gen(timeout)
        self._events_queue.extend(
            self.process_events(events_gen)
        )

        while self._events_queue:
            yield self._events_queue.popleft()


class OutputWrapper:

    CONSOLE_CLS = None
    ROOT_PANEL_CLS = RootPanel

    def __init__(self, colors_manager):
        self.colors_manager = colors_manager

    def create_console(self, size):
        return self.CONSOLE_CLS(size)

    def create_panel(self, size):
        console = self.create_console(size)
        return self.ROOT_PANEL_CLS(console, self.colors_manager)

    def render(self, panel):
        """Show contents of given panel on screen."""
        raise NotImplementedError()


class IOWrapper:

    def __init__(self,
        console_size,
        colors_manager,
        title=None,
        *args, **kwargs,
    ):
        self.title = title
        self.console_size = console_size
        self.colors_manager = colors_manager
        self._input = None
        self._output = None

    def set_palette(self, palette):
        self.colors_manager.palette = palette

    @property
    def is_initialized(self):
        return False

    def initialize(self):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()

    def create_panel(self, size=None):
        return self._output.create_panel(size or self.console_size)

    def render(self, panel):
        """Render contents of given panel on screen."""
        if not self.is_initialized:
            self.initialize()
        self._output.render(panel)

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

