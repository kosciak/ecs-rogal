import functools

import tcod

from ..console import DEFAULT_CH, Alignment, RootPanel
from ..events.keys import Key

from .core import IOWrapper


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
        key = TCOD_KEYS.get(sym, str(sym))
    return Key.with_modifiers(
        key,
        ctrl=mod & tcod.event.KMOD_CTRL,
        alt=mod & tcod.event.KMOD_ALT,
        shift=mod & tcod.event.KMOD_SHIFT,
    )

# Monkey patch KeyboardEvent by adding key property for event details translation
tcod.event.KeyboardEvent.key = property(lambda self: get_key(self.sym, self.mod))


class TcodRootPanel(RootPanel):

    def __str__(self):
        return str(self.console)

    def clear(self, colors=None, *args, **kwargs):
        fg = self.rgb(colors and colors.fg) or self.palette.fg.rgb
        bg = self.rgb(colors and colors.bg) or self.palette.bg.rgb
        return self._clear(fg=fg, bg=bg, *args, **kwargs)

    def print(self, text, position, colors=None, alignment=None, *args, **kwargs):
        # NOTE: Do NOT change already set colors!
        fg = self.rgb(colors and colors.fg)
        bg = self.rgb(colors and colors.bg)
        alignment = alignment or Alignment.LEFT
        return self._print(
            position.x, position.y, text, fg=fg, bg=bg, alignment=alignment, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        fg = self.rgb(tile.fg)
        bg = self.rgb(tile.bg)
        if size:
            return self._draw_rect(
                position.x, position.y, size.width, size.height,
                ch=tile.ch, fg=fg, bg=bg, *args, **kwargs)
        else:
            return self._print(
                position.x, position.y, tile.char, fg=fg, bg=bg, *args, **kwargs)

    def image(self, image, position, *args, **kwargs):
        return self._draw_semigraphics(
            image, position.x, position.y, *args, **kwargs)

    # TODO: Needs rework using Position, Size!
    def blit_from(self, x, y, src, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: src MUST be tcod.Console!
        src.blit(dest=self.console, dest_x=x, dest_y=y, *args, **kwargs)

    def blit_to(self, x, y, dest, *args, **kwargs):
        # RULE: Use keyword arguments for dest_x, dest_y, width height
        # NOTE: dest MUST be tcod.Console!
        self.console.blit(dest=dest, src_x=x, src_y=y, *args, **kwargs)

    # NOTE: tcod.Console print/draw related methods:

    def _put_char(self, x, y, ch, *args, **kwargs):
        """tcod.Console.put_char(
            x: int, y: int, 
            ch: int, 
            bg_blend: int = 13)
        """
        return self.console.put_char(x, y, ch, *args, **kwargs)

    def _print(self, x, y, text, fg=None, bg=None, *args, **kwargs):
        """tcod.Cosole.print(
            x: int, y: int, 
            string: str, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1, 
            alignment: int = 0)
        """
        return self.console.print(
            x, y, text, fg=fg, bg=bg, *args, **kwargs)

    def _print_box(self, x, y, width, height, text, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.print_box(
            x: int, y: int, 
            width: int, height: int, 
            string: str, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1, 
            alignment: int = 0)-> int
        """
        return self.console.print_box(
            x, y, width, height, text, fg=fg, bg=bg, *args, **kwargs)

    def _get_height_rect(self, x, y, width, height, text, *args, **kwargs):
        """tcod.Console.get_height_rect(
            x: int, y: int, 
            width: int, height: int, 
            string: str)-> int
        """
        return self.console.get_height_rect(
            x, y, width, height, text, *args, **kwargs)

    def _draw_rect(self, x, y, width, height, ch, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.draw_rect(
            x: int, y: int, 
            width: int, height: int, 
            ch: int, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1)
        """
        return self.console.draw_rect(
            x, y, width, height, ch, fg=fg, bg=bg, *args, **kwargs)

    def _draw_frame(self, x, y, width, height, title=None, clear=True, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.draw_frame(
            x: int, y: int, 
            width: int, height: int, 
            title: str = '', 
            clear: bool = True, 
            fg: Optional[Tuple[int, int, int]] = None, 
            bg: Optional[Tuple[int, int, int]] = None, 
            bg_blend: int = 1)
        """
        title = title or ''
        return self.console.draw_frame(
            x, y, width, height, title=title, clear=clear, fg=fg, bg=bg, *args, **kwargs)

    def _draw_semigraphics(self, pixels, x, y, *args, **kwargs):
        """tcod.Console.draw_semigraphics(
            pixels: Any, 
            x: int = 0, 
            y: int = 0)
        """
        return self.console.get_height_rect(pixels, x, y, *args, **kwargs)

    def _clear(self, ch=None, fg=None, bg=None, *args, **kwargs):
        """tcod.Console.clear(
            ch: int = 32, 
            fg: Tuple[int, int, int] = Ellipsis, 
            bg: Tuple[int, int, int] = Ellipsis)
        """
        ch = ch or DEFAULT_CH
        return self.console.clear(ch, fg=fg, bg=bg, *args, **kwargs)

    # blit(
    #   dest: tcod.console.Console, 
    #   dest_x: int = 0, dest_y: int = 0, 
    #   src_x: int = 0, src_y: int = 0, 
    #   width: int = 0, height: int = 0, 
    #   fg_alpha: float = 1.0, 
    #   bg_alpha: float = 1.0, 
    #   key_color: Optional[Tuple[int, int, int]] = None)

    # TODO: Direct access to console.tiles, console.tiles_rgb fragments
    # NOTE: you can acces bg, fg, chr as tiles_rgb['bg'], tiles_rgb['fg'], tiles['ch']

    @property
    def tiles(self):
        """Translate coordinates relative to self, to coordinates relative to root."""
        return self.parent.tiles[self.x:self.x2, self.y:self.y2]

    @tiles.setter
    def tiles(self, tiles):
        self.parent.tiles[self.x:self.x2, self.y:self.y2] = tiles

    @property
    def tiles_rgb(self):
        return self.parent.tiles_rgb[self.x:self.x2, self.y:self.y2]

    @tiles_rgb.setter
    def tiles_rgb(self, tiles_rgb):
        self.parent.tiles_rgb[self.x:self.x2, self.y:self.y2] = tiles_rgb

    def show(self):
        from . import ansi
        ansi.show_tcod_console(self.console)



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
    def is_initialized(self):
        return self._context is not None

    @property
    def context(self):
        if not self.is_initialized:
            context = tcod.context.new(
                columns=self.console_size.width,
                rows=self.console_size.height,
                title=self.title,
                tileset=self.tilesheet,
                sdl_window_flags=self.resizable and tcod.context.SDL_WINDOW_RESIZABLE
            )
            self._context = context
        return self._context

    def load_tilesheet(self, tilesheet):
        return tcod.tileset.load_tilesheet(
            tilesheet.path, tilesheet.columns, tilesheet.rows, tilesheet.charmap)

    @property
    def tilesheet(self):
        return self.load_tilesheet(self._tilesheet)

    @tilesheet.setter
    def tilesheet(self, tilesheet):
        self._tilesheet = tilesheet
        if self.is_initialized:
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
        if isinstance(console, RootPanel):
            console = console.console
        if self.is_initialized:
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
        if self.is_initialized:
            self.context.close()
            self._context = None

