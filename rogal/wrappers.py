import functools

from .keys import Key

import tcod

from .ui import TcodRootPanel


TCOD_KEYS = {
    tcod.event.K_ESCAPE: Key.ESCAPE,

    tcod.event.K_F1: Key.F1,
    tcod.event.K_F2: Key.F2,
    tcod.event.K_F3: Key.F3,
    tcod.event.K_F4: Key.F4,
    tcod.event.K_F5: Key.F5,
    tcod.event.K_F6: Key.F6,
    tcod.event.K_F7: Key.F7,
    tcod.event.K_F8: Key.F8,
    tcod.event.K_F9: Key.F9,
    tcod.event.K_F10: Key.F10,
    tcod.event.K_F11: Key.F11,
    tcod.event.K_F12: Key.F12,

    tcod.event.K_BACKSPACE: Key.BACKSPACE,

    tcod.event.K_TAB: Key.TAB,

    tcod.event.K_RETURN: Key.RETURN,

    tcod.event.K_SPACE: Key.SPACE,

    tcod.event.K_UP: Key.UP,
    tcod.event.K_DOWN: Key.DOWN,
    tcod.event.K_LEFT: Key.LEFT,
    tcod.event.K_RIGHT: Key.RIGHT,

    tcod.event.K_INSERT: Key.INSERT,
    tcod.event.K_DELETE: Key.DELETE,
    tcod.event.K_HOME: Key.HOME,
    tcod.event.K_END: Key.END,
    tcod.event.K_PAGEUP: Key.PAGE_UP,
    tcod.event.K_PAGEDOWN: Key.PAGE_DOWN,

    tcod.event.K_KP_0: Key.KP_0,
    tcod.event.K_KP_1: Key.KP_1,
    tcod.event.K_KP_2: Key.KP_2,
    tcod.event.K_KP_3: Key.KP_3,
    tcod.event.K_KP_4: Key.KP_4,
    tcod.event.K_KP_5: Key.KP_5,
    tcod.event.K_KP_6: Key.KP_6,
    tcod.event.K_KP_7: Key.KP_7,
    tcod.event.K_KP_8: Key.KP_8,
    tcod.event.K_KP_9: Key.KP_9,

    tcod.event.K_KP_DIVIDE: Key.KP_DIVIDE,
    tcod.event.K_KP_MULTIPLY: Key.KP_MULTIPLY,
    tcod.event.K_KP_MINUS: Key.KP_MINUS,
    tcod.event.K_KP_PLUS: Key.KP_PLUS,
    tcod.event.K_KP_ENTER: Key.KP_ENTER,
    tcod.event.K_KP_PERIOD: Key.KP_PERIOD,
    tcod.event.K_KP_COMMA: Key.KP_COMMA,
    tcod.event.K_KP_CLEAR: Key.CLEAR,
}


@functools.lru_cache(maxsize=None)
def get_key(sym, mod):
    if 32 <= sym <= 126:
        key = chr(sym)
    else:
        key = TCOD_KEYS.get(sym, Key.UNKNOWN)
    return Key.with_modifiers(
        key,
        ctrl=mod & tcod.event.KMOD_CTRL,
        alt=mod & tcod.event.KMOD_ALT,
        shift=mod & tcod.event.KMOD_SHIFT,
    )

# Monkey path KeyboardEvent by adding key property for event details translation
tcod.event.KeyboardEvent.key = property(lambda self: get_key(self.sym, self.mod))


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

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


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

