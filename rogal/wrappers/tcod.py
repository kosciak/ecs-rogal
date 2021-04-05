import functools
import logging

import tcod
from tcod.loader import ffi, lib

from ..console import DEFAULT_CH, Align, RootPanel
from ..events import EventType

from .core import IOWrapper
from . import sdl


log = logging.getLogger(__name__)


sdl2 = sdl.SDL2Wrapper(ffi, lib)


class TcodRootPanel(RootPanel):

    def __str__(self):
        return str(self.console)

    def clear(self, colors=None, *args, **kwargs):
        fg = self.rgb(colors and colors.fg) or self.palette.fg.rgb
        bg = self.rgb(colors and colors.bg) or self.palette.bg.rgb
        return self._clear(fg=fg, bg=bg, *args, **kwargs)

    def print(self, text, position, colors=None, align=None, *args, **kwargs):
        # NOTE: Do NOT change already set colors!
        fg = self.rgb(colors and colors.fg)
        bg = self.rgb(colors and colors.bg)
        align = align or Align.LEFT
        return self._print(
            position.x, position.y, text, fg=fg, bg=bg, alignment=align, *args, **kwargs)

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
        tileset,
        resizable=False,
        title=None,
        enable_joystick=False,
    ):
        self.console_size = console_size
        self._palette = palette
        self._tileset = tileset
        self.resizable = resizable
        self.title=title
        self._context = None
        self.enable_joystick = enable_joystick

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
                tileset=self.tileset,
                sdl_window_flags=self.resizable and tcod.context.SDL_WINDOW_RESIZABLE
            )
            self._context = context
            if self.enable_joystick:
                self.init_joystick()
        return self._context

    def load_tilesheet(self, tilesheet):
        return tcod.tileset.load_tilesheet(
            tilesheet.path, tilesheet.columns, tilesheet.rows, tilesheet.charmap)

    def load_truetype_font(self, truetype_font):
        # TODO: Check: https://github.com/libtcod/python-tcod/blob/develop/examples/ttf.py
        #       For improved support for TTF fonts
        return tcod.tileset.load_truetype_font(
            truetype_font.path, truetype_font.width, truetype_font.height)

    def load_tileset(self, tileset):
        if tileset.path.endswith('.ttf'):
            return self.load_truetype_font(tileset)
        else:
            return self.load_tilesheet(tileset)

    @property
    def tileset(self):
        return self.load_tileset(self._tileset)

    @tileset.setter
    def tileset(self, tileset):
        self._tileset = tileset
        if self.is_initialized:
            tileset = self.load_tileset(self._tileset)
            self.context.change_tileset(tileset)

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

    def init_joystick(self):
        # See: https://wiki.libsdl.org/SDL_JoystickOpen
        log.debug('Initializing joystick...')
        sdl2.SDL_InitSubSystem(sdl.SDL_SubSystem.SDL_INIT_JOYSTICK)
        joysticks_num = sdl2.SDL_NumJoysticks()
        log.debug(f'Found {joysticks_num} joysticks')
        if not joysticks_num:
            return
        joystick_id = 0
        log.debug(f'Opening joystick: {joystick_id}')
        joystick = sdl2.SDL_JoystickOpen(joystick_id)
        if not joystick:
            log.error(f'Failed to open joystick: {joystick_id}')
            return
        name = sdl2.SDL_JoystickNameForIndex(joystick_id)
        axes_num = sdl2.SDL_JoystickNumAxes(joystick)
        buttons_num = sdl2.SDL_JoystickNumButtons(joystick)
        balls_num = sdl2.SDL_JoystickNumBalls(joystick)
        hats_num = sdl2.SDL_JoystickNumHats(joystick)
        log.info(f'Joystick: {joystick_id} - name: {name}, axes: {axes_num}, buttons: {buttons_num}, balls: {balls_num}, hats: {hats_num}')

    def set_system_cursor(self, cursor_id=sdl.SDL_SystemCursor.SDL_SYSTEM_CURSOR_ARROW):
        # See: https://wiki.libsdl.org/SDL_CreateSystemCursor
        cursor = sdl2.SDL_CreateSystemCursor(cursor_id)
        sdl2.SDL_SetCursor(cursor)

    def update_event(self, event):
        if event.type == EventType.MOUSE_MOTION or \
           event.type == EventType.MOUSE_BUTTON_PRESS or\
           event.type == EventType.MOUSE_BUTTON_UP:
            x, y = self.context.pixel_to_tile(*event.pixel_position)
            event.set_tile(x, y)
        if event.type == EventType.MOUSE_MOTION:
            prev_position = event.pixel_position.moved_from(event.pixel_motion)
            prev_x, prev_y = self.context.pixel_to_tile(*prev_position)
            dx = event.position.x - prev_x
            dy = event.position.y - prev_y
            event.set_tile_motion(dx, dy)
        return event

    def events(self, wait=None):
        # TODO: wrappers.sdl and create rogal.events.core directly from sld events?
        if wait is False:
            events_gen = sdl2.get_events()
        else:
            # NOTE: wait==None will wait forever
            if wait is True:
                wait = None
            events_gen = sdl2.wait_for_events(wait)
        for event in events_gen:
            # Intercept WINDOW RESIZE and update self.console_size?
            event = self.update_event(event)
            yield event

    def close(self):
        if self.is_initialized:
            self.context.close()
            self._context = None

