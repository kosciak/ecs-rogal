import logging

import tcod
from tcod.loader import ffi, lib

from ...geometry import Size

from ...tiles_sources.box_drawing import BoxDrawing
from ...tiles_sources.block_elements import BlockElements

from ..core import IOWrapper

from ..sdl.sdl2 import SDL2
from ..sdl.const import SDL_SystemCursor

from .input import TcodSDLInputWrapper
from .output import TcodOutputWrapper
# from .output import TcodNaiveOutputWrapper


log = logging.getLogger(__name__)


sdl2 = SDL2(ffi, lib)


class TilesLoader:

    def __init__(self, tiles_sources):
        self.tiles_sources = tiles_sources
        self.tileset = None

    @property
    def tile_size(self):
        if self.tileset:
            return Size(self.tileset.tile_width, self.tileset.tile_height)

    def create_tileset(self, tile_size):
        tileset = tcod.tileset.Tileset(*tile_size)
        return tileset

    def load_tilesheet(self, tilesheet):
        return tcod.tileset.load_tilesheet(
            tilesheet.path, tilesheet.columns, tilesheet.rows, tilesheet.charset)

    def load_tiles_gen(self, tiles_source):
        for code_point, tile in tiles_source.tiles_gen(self.tile_size):
            if tile is None:
                continue
            self.tileset.set_tile(code_point, tile)
        return self.tileset

    def load(self):
        for tiles_source in self.tiles_sources:
            if tiles_source.is_tilesheet:
                # TODO: Combining multiple tilesheets
                self.tileset = self.load_tilesheet(tiles_source)
                continue
            if not self.tileset:
                self.tileset = self.create_tileset(tiles_source.tile_size)
            self.load_tiles_gen(tiles_source)
        return self.tileset


class TcodWrapper(IOWrapper):

    def __init__(self,
        console_size,
        colors_manager,
        tiles_sources,
        resizable=False,
        title=None,
        enable_joystick=False,
    ):
        super().__init__(console_size=console_size, colors_manager=colors_manager, title=title)
        self._context = None
        self.tiles_loader = TilesLoader(tiles_sources)
        self.resizable = resizable
        self.enable_joystick = enable_joystick

    @property
    def is_initialized(self):
        return self._context is not None

    def initialize_context(self):
        context = tcod.context.new(
            columns=self.console_size.width,
            rows=self.console_size.height,
            title=self.title,
            tileset=self.tiles_loader.load(),
            sdl_window_flags=self.resizable and tcod.context.SDL_WINDOW_RESIZABLE
        )
        return context

    @property
    def context(self):
        if not self.is_initialized:
            self.initialize()
        return self._context

    def initialize(self):
        # TODO: Why joystick initialization is done before initializing context?
        if self.enable_joystick:
            self.initialize_joystick()
        self._context = self.initialize_context()

        self._input = TcodSDLInputWrapper(sdl2, self.context)
        self._output = TcodOutputWrapper(self.context, self.colors_manager)
        # self._output = TcodNaiveOutputWrapper(self.context, self.colors_manager)

    def terminate(self):
        self.context.close()
        self._context = None

    # TODO: Move methods below elsewhere...

    def initialize_joystick(self):
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

    def set_system_cursor(self, cursor_id=SDL_SystemCursor.SDL_SYSTEM_CURSOR_ARROW):
        # See: https://wiki.libsdl.org/SDL_CreateSystemCursor
        cursor = sdl2.SDL_CreateSystemCursor(cursor_id)
        sdl2.SDL_SetCursor(cursor)

