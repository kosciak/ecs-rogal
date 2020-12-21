import tcod

from .ui import TcodRootPanel


class IOWrapper:

    def create_console(self, size=None):
        return None

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


class TcodWrapper(IOWrapper):

    def __init__(self, 
        console_size,
        palette,
        tilesheet,
        resizable=False,
        title=None,
    ):
        self.console_size = console_size
        self._palette = palette
        self._tilesheet = tilesheet
        self.resizable = resizable
        self.title=title
        self._context = None

    @property
    def initialized(self):
        return self._context is not None

    @property
    def context(self):
        if not self.initialized:
            context = tcod.context.new(
                columns=self.console_size.width,
                rows=self.console_size.height,
                title=self.title,
                tileset=self.tilesheet,
                sdl_window_flags=self.resizable and tcod.context.SDL_WINDOW_RESIZABLE
            )
            self._context = context
        return self._context

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, palette):
        # TODO: Some event on palette change forcing everything to redraw?
        self._palette = palette  

    def load_tilesheet(self, tilesheet):
        return tcod.tileset.load_tilesheet(
            tilesheet.path, tilesheet.columns, tilesheet.rows, tilesheet.charmap)

    @property
    def tilesheet(self):
        return self.load_tilesheet(self._tilesheet)

    @tilesheet.setter
    def tilesheet(self, tilesheet):
        self._tilesheet = tilesheet
        if self.initialized:
            tilesheet = self.load_tilesheet(self._tilesheet)
            self.context.change_tilesheet(tilesheet)

    def create_console(self, size=None):
        # TODO: Check options and resizing behaviour
        size = size or self.console_size
        # NOTE: new_console returns console with order=="C"
        return self.context.new_console(*size)

    def create_panel(self, size=None):
        console = self.create_console(size)
        return TcodRootPanel(console, self.palette)

    def flush(self, console):
        if not isinstance(console, tcod.console.Console):
            console = console.console
        if self.initialized:
            # TODO: Check options and resizing behaviour
            self.context.present(console)

    def events(self, wait=None):
        if wait is False:
            event_gen = tcod.event.get()
        else:
            # NOTE: wait==None will wait forever
            if wait is True:
                wait = None
            event_gen = tcod.event.wait(wait)
        for event in event_gen:
            # Intercept WINDOW RESIZE and update self.console_size?
            self.context.convert_event(event)
            yield event

    def close(self):
        if self.initialized:
            self.context.close()
            self._context = None


class MockWrapper(IOWrapper):

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
        size = size or self.console_size
        # NOTE: Use order="C" to match context.new_console behaviour
        return tcod.console.Console(*size, order="C")

    def create_panel(self, size=None):
        console = self.create_console(size)
        return TcodRootPanel(console, self.palette)

    def flush(self, console):
        if not isinstance(console, tcod.console.Console):
            console = console.console
        from . import ansi
        ansi.show_tcod_console(console)
