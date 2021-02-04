import numpy as np

from .. import dtypes


class IOWrapper:

    def __init__(self,
        console_size,
        palette,
    ):
        self.console_size = console_size
        self._palette = palette

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, palette):
        # TODO: Some event on palette change forcing everything to redraw?
        self._palette = palette

    def create_console(self, size=None):
        if not size:
            return None
        return np.zeros(size, dtype=dtypes.rgb_console_dt)

    def create_panel(self, size=None):
        return None

    def flush(self, console):
        return

    def events(self, wait=.0):
        yield from ()

    def __enter__(self):
        return self

    def close(self):
        return

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class MockWrapper(IOWrapper):

    def create_console(self, size=None):
        import tcod
        size = size or self.console_size
        # NOTE: Use order="C" to match context.new_console behaviour
        return tcod.console.Console(*size, order="C")

    def create_panel(self, size=None):
        from .tcod import TcodRootPanel
        console = self.create_console(size)
        return TcodRootPanel(console, self.palette)

    def flush(self, console):
        if not isinstance(console, tcod.console.Console):
            console = console.console
        from . import ansi
        ansi.show_tcod_console(console)

