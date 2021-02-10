from ..ui import Console, RootPanel


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
        return Console(size)

    def create_panel(self, size=None):
        console = self.create_console(size)
        return RootPanel(console, self.palette)

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

    def flush(self, console):
        if isinstance(console, RootPanel):
            console = console.console
        from . import ansi
        ansi.show_console(console)

