import functools
import logging

import tcod
from tcod.loader import ffi, lib

from ..console import DEFAULT_CH, Align, RootPanel
from ..events import EventType

from ..tiles.fonts import TrueTypeFont
from ..tiles.box_drawing import BoxDrawing
from ..tiles.box_elements import BoxElements

from .core import IOWrapper

from . import sdl
from .sdl_input import SDLInputWrapper


log = logging.getLogger(__name__)


sdl2 = sdl.SDL2(ffi, lib)


MOUSE_EVENT_TYPES = {
    EventType.MOUSE_MOTION,
    EventType.MOUSE_BUTTON_PRESS,
    EventType.MOUSE_BUTTON_UP,
}


# TODO: Move to tcod_display?
class TcodRootPanel(RootPanel):

    def __str__(self):
        return str(self.console)

    def clear(self, colors=None, *args, **kwargs):
        fg = self.get_color(colors and colors.fg) or self.palette.fg.rgb
        bg = self.get_color(colors and colors.bg) or self.palette.bg.rgb
        return self._clear(fg=fg, bg=bg, *args, **kwargs)

    def print(self, text, position, colors=None, align=None, *args, **kwargs):
        # NOTE: Do NOT change already set colors!
        fg = self.get_color(colors and colors.fg)
        bg = self.get_color(colors and colors.bg)
        align = align or Align.LEFT
        return self._print(
            position.x, position.y, text, fg=fg, bg=bg, alignment=align, *args, **kwargs)

    def draw(self, tile, position, size=None, *args, **kwargs):
        fg = self.get_color(tile.fg)
        bg = self.get_color(tile.bg)
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
        from ..term import ansi
        ansi.show_rgb_console(self.console)


class TcodSDLInputWrapper(SDLInputWrapper):

    def __init__(self, context):
        super().__init__(sdl2=sdl2)
        self.context = context

    def update_mouse_event(self, event):
        pixel_position = event.position
        x, y = self.context.pixel_to_tile(*pixel_position)
        event.set_position(x, y)
        event.set_pixel_position(*pixel_position)

        if event.type == EventType.MOUSE_MOTION:
            pixel_motion = event.motion
            prev_position = event.pixel_position.moved_from(pixel_motion)
            prev_x, prev_y = self.context.pixel_to_tile(*prev_position)
            dx = event.position.x - prev_x
            dy = event.position.y - prev_y
            event.set_motion(dx, dy)
            event.set_pixel_motion(*pixel_motion)

        return event

    def process_mouse_position(self, events_gen):
        for event in events_gen:
            if event.type in MOUSE_EVENT_TYPES:
                event = self.update_mouse_event(event)
            yield event


class TcodWrapper(IOWrapper):

    ROOT_PANEL_CLS = TcodRootPanel

    def __init__(self,
        console_size,
        palette,
        tileset,
        resizable=False,
        title=None,
        enable_joystick=False,
    ):
        super().__init__(console_size=console_size, palette=palette, title=title)
        self._tileset = tileset
        self.resizable = resizable
        self._context = None
        self.enable_joystick = enable_joystick

    @property
    def is_initialized(self):
        return self._context is not None

    def initialize(self):
        context = tcod.context.new(
            columns=self.console_size.width,
            rows=self.console_size.height,
            title=self.title,
            tileset=self.tileset,
            sdl_window_flags=self.resizable and tcod.context.SDL_WINDOW_RESIZABLE
        )
        if self.enable_joystick:
            self.init_joystick()
        self._context = context
        self._input = TcodSDLInputWrapper(self._context)

    def terminate(self):
        self.context.close()
        self._context = None

    @property
    def context(self):
        if not self.is_initialized:
            self.initialize()
        return self._context

    def load_tilesheet(self, tilesheet):
        return tcod.tileset.load_tilesheet(
            tilesheet.path, tilesheet.columns, tilesheet.rows, tilesheet.charmap)

    def load_truetype_font_obsolete(self, truetype_font):
        return tcod.tileset.load_truetype_font(
            truetype_font.path, truetype_font.width, truetype_font.height)

    def load_truetype_font(self, font):
        # See: Check: https://github.com/libtcod/python-tcod/blob/develop/examples/ttf.py
        #       For improved support for TTF fonts
        import freetype
        import numpy as np

        ttf = freetype.Face(font.path)
        ttf.set_pixel_sizes(font.width, font.height)
        tileset = tcod.tileset.Tileset(font.width, font.height)
        for codepoint, glyph_index in ttf.get_chars():
            ttf.load_glyph(glyph_index)
            bitmap = ttf.glyph.bitmap
            assert bitmap.pixel_mode == freetype.FT_PIXEL_MODE_GRAY
            bitmap_array = np.asarray(bitmap.buffer).reshape(
                (bitmap.width, bitmap.rows), order="F"
            )
            if bitmap_array.size == 0:
                continue  # Skip blank glyphs.
            output_image = np.zeros((font.width, font.height), dtype=np.uint8, order="F")
            out_slice = output_image

            # Adjust the position to center this glyph on the tile.
            # TODO: Seems to be messing up box drawing chars...
            left = (font.width - bitmap.width) // 2
            top = font.height - ttf.glyph.bitmap_top + ttf.size.descender // 64

            # `max` is used because I was too lazy to properly slice the array.
            out_slice = out_slice[max(0, left) :, max(0, top) :]
            out_slice[
                : bitmap_array.shape[0], : bitmap_array.shape[1]
            ] = bitmap_array[: out_slice.shape[0], : out_slice.shape[1]]

            tileset.set_tile(codepoint, output_image.transpose())
        # TODO: Need some fallback for missing glyphs
        return tileset

    def load_ttf_font(self, font):
        ttf = TrueTypeFont(font.path)
        ttf.set_char_size(font.size)
        tile_size = ttf.pixel_size

        tiles_sources = [
            ttf,
            BoxDrawing(),
            BoxElements(),
        ]

        tileset = tcod.tileset.Tileset(*tile_size)
        for code_point in font.charmap:
            for source in tiles_sources:
                if not source.has_code_point(code_point):
                    continue
                tile = source.get_tile(code_point, tile_size)
                if tile is None:
                    continue
                tileset.set_tile(code_point, tile)

        return tileset

    def load_tileset(self, tileset):
        if tileset.path.endswith('.ttf'):
            # return self.load_truetype_font(tileset)
            return self.load_ttf_font(tileset)
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

    def flush(self, panel):
        if self.is_initialized:
            # TODO: Check options and resizing behaviour
            self.context.present(panel.console)

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

