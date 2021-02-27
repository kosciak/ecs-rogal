import logging
import time

import numpy as np

from . import logs

from . import bitmask
from . import components
from .ecs import System, RunState
from .geometry import Rectangular, Position, Size, Rectangle
from .tiles import RenderOrder, Colors, Tile
from . import terrain

from .console import Align
from .console import toolkit
from .console import ui

from .utils import perf


log = logging.getLogger(__name__)


"""Rendering components."""


CAMERA_SIZE = Size(15, 15)
CAMERA_SIZE = Size(26, 26)

SCROLLABLE_CAMERA = True
SCROLLABLE_CAMERA = False

SHOW_BOUNDARIES = True


class ConsoleWindowsSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

        self.wrapper = self.ecs.resources.wrapper
        self._root = None

    @property
    def root(self):
        if self.ecs.resources.root_panel is None:
            self.ecs.resources.root_panel = self.wrapper.create_panel()
        self._root = self.ecs.resources.root_panel
        return self._root

    def init_windows(self):
        to_create = self.ecs.manage(components.CreateWindow)
        to_create.insert(self.ecs.create(), 'IN_GAME')

    def create_windows(self):
        to_create = self.ecs.manage(components.CreateWindow)
        window_renderers = self.ecs.manage(components.WindowRenderers)
        panel_renderers = self.ecs.manage(components.PanelRenderer)

        layouts = []
        for window, name in to_create:
            if name == 'QUIT_YES_NO_PROMPT':
                layout = ui.YesNoPrompt(title='Quit?', msg='Are you sure you want to quit?')
                layouts.append([window, layout, self.root])

            if name == 'IN_GAME':
                cam_panel, msg_log_panel = self.root.split(bottom=12)
                # cam_panel = self.root.create_panel(Position(10,10), CAMERA_SIZE)
                layout = ui.Window(title='logs')
                widget = MessageLog()
                layout.content.append(widget)
                layouts.append([window, layout, msg_log_panel])

                layout = ui.Window(title='mapcam')
                widget = Camera(self.ecs)
                layout.content.append(widget)
                layouts.append([window, layout, cam_panel])

        for window, layout, panel in layouts:
            renderers = window_renderers.insert(window)
            for renderer in layout.layout(panel):
                renderer_id = self.ecs.create()
                renderers.add(renderer_id)
                panel_renderers.insert(renderer_id, renderer)

        to_create.clear()

    def destroy_windows(self):
        to_destroy = self.ecs.manage(components.DestroyWindow)
        window_renderers = self.ecs.manage(components.WindowRenderers)

        for window, renderers in self.ecs.join(to_destroy.entities, window_renderers):
            self.ecs.remove(*renderers)
        self.ecs.remove(*to_destroy.entities)
        to_destroy.clear()

    def run(self):
        if self.ecs.run_state == RunState.PRE_RUN:
            self.init_windows()
        self.destroy_windows()
        self.create_windows()


class ConsoleRenderingSystem(System):

    FPS = 35

    def __init__(self, ecs):
        super().__init__(ecs)

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self.wrapper = self.ecs.resources.wrapper
        self._root = None

        self._last_run = None
        self._fps = None
        self.frame = None
        self.fps = self.FPS

        self.player = None

    @property
    def root(self):
        if self.ecs.resources.root_panel is None:
            self.ecs.resources.root_panel = self.wrapper.create_panel()
        self._root = self.ecs.resources.root_panel
        return self._root

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        self.frame = 1./self._fps

    def should_run(self, state):
        now = time.time()
        if self._last_run and now - self._last_run < self.frame:
            # Do NOT render more often than once a frame
            return False
        self._last_run = now
        return True

    def render(self):
        # Clear panel
        self.root.clear(self.default_colors)

        # Render all panels
        renderers = self.ecs.manage(components.PanelRenderer)
        for panel, renderer in renderers:
            with perf.Perf(renderer.renderer.render):
                renderer.clear(self.default_colors)
                renderer.render()

        # Show rendered panel
        self.wrapper.flush(self.root)

    def run(self):
        if not self.ecs.resources.current_player:
            return False

        self.render()
        return True


class Camera(Rectangular, toolkit.Renderer):

    def __init__(self, ecs,
                 scrollable=SCROLLABLE_CAMERA, show_boundaries=SHOW_BOUNDARIES):
        super().__init__()
        self.ecs = ecs
        self.spatial = self.ecs.resources.spatial

        self.tileset = self.ecs.resources.tileset

        self.position = Position.ZERO

        self.scrollable = scrollable
        self.show_boundaries = show_boundaries

        self.walls_terrain_type = terrain.Type.WALL
        self.bitmasked_walls = self.tileset.bitmasks['WALLS_DLINE']

    def calc_position(self, level, position=None):
        """Select what camera should be centered on."""
        if not position or not self.scrollable:
            # Use center of given level
            position = level.center
        self.position = Position(
            position.x-self.panel.width//2,
            position.y-self.panel.height//2
        )

        # For level-centered camera need to move camera if level.size > camera.size and approaching edge
        # TODO: Test it, and... 
        # TODO: Maybe use viewshed.view_range for adjustments? Whole viewshed should be rendered
        # Adjust top-left corner
        adjusted_position = Position(
            min(self.x, position.x-1),
            min(self.y, position.y-1)
        )
        # Adjust bottom-right corner
        adjust_move = Position(
        max(0, 2+position.x-self.x2),
        max(0, 2+position.y-self.y2),
        )
        self.position = adjusted_position + adjust_move

    def get_coverage(self, level):
        """Return part of the level that is covered by camera."""
        coverage = self & level
        return coverage

    def get_covered(self, array, coverage):
        """Return covered part of an array."""
        return array[
            coverage.x : coverage.x2,
            coverage.y : coverage.y2
        ]

    def walls_bitmask(self, level_id, coverage, revealed, terrain_type):
        walls_mask = self.spatial.terrain_type(level_id, terrain_type)
        walls_mask = self.get_covered(walls_mask, coverage)
        # NOTE: We don't want bitmasking to spoil not revealed terrain!
        return bitmask.bitmask_walls(walls_mask, revealed)

    def draw_boundaries(self, level_size):
        """Draw BOUNDARIES of the level."""
        if not self.show_boundaries:
            return
        boundaries = set()
        for boundary in [
            Rectangle(Position(-1,-1), Size(level_size.width+2, 1)),
            Rectangle(Position(-1,level_size.height), Size(level_size.width+2, 1)),
            Rectangle(Position(-1, 0), Size(1, level_size.height)),
            Rectangle(Position(level_size.width, 0), Size(1, level_size.height)),
        ]:
            intersection = self & boundary
            if intersection:
                boundaries.update(intersection.positions)
        for position in boundaries:
            tile = self.tileset.get('BOUNDARY').visible
            self.panel.draw(tile, position.offset(self.position))

    def draw_terrain_tile(self,
        terrain_mask, visible, revealed, mask_offset,
        renderable, ch=None,
    ):
        # Visible
        mask = terrain_mask & visible
        if np.any(mask):
            tile = renderable.tile_visible
            if ch is not None:
                tile = Tile.create(ch, tile.fg, tile.bg)
            self.panel.mask(tile, mask, mask_offset)

        # Revealed but not visible
        mask = terrain_mask & revealed
        if np.any(mask):
            tile = renderable.tile_revealed
            if ch is not None:
                tile = Tile.create(ch, tile.fg, tile.bg)
            self.panel.mask(tile, mask, mask_offset)

    def draw_bitmasked_terrain_tile(self,
        walls_mask, terrain_mask, visible, revealed, mask_offset,
        renderable,
    ):
        for bitmask_value in np.unique(walls_mask):
            ch = self.bitmasked_walls[bitmask_value]
            mask = terrain_mask & (walls_mask == bitmask_value)
            self.draw_terrain_tile(
                mask, visible, revealed, mask_offset,
                renderable, ch,
            )

    def draw_terrain(self, level_id, terrain, coverage, revealed, visible):
        """Draw TERRAIN tiles."""

        # Bitshift masking for terrain.Type.WALL terrain
        walls_mask = self.walls_bitmask(level_id, coverage, revealed, self.walls_terrain_type)

        # Offset for drawing a terrain tile with a mask
        # It's mirrored camera.position but only with x,y values > 0
        mask_offset = Position(max(0, self.x*-1), max(0, self.y*-1))

        revealed_not_visible = revealed ^ visible

        renderables = self.ecs.manage(components.Renderable)
        for terrain_id in np.unique(terrain):
            if not terrain_id:
                continue

            terrain_mask = terrain == terrain_id
            renderable = renderables.get(terrain_id)
            if not renderable:
                continue

            if terrain_id >> 4 == self.walls_terrain_type:
                self.draw_bitmasked_terrain_tile(
                    walls_mask,
                    terrain_mask, visible, revealed_not_visible, mask_offset,
                    renderable,
                )
            else:
                self.draw_terrain_tile(
                    terrain_mask, visible, revealed_not_visible, mask_offset,
                    renderable,
                )

    def draw_entities(self, level_id, coverage, revealed, visible):
        """Draw all renderable ENTITIES, in order described by Renderable.render_order."""
        renderables = self.ecs.manage(components.Renderable)
        locations = self.ecs.manage(components.Location)

        entities = self.spatial.entities(level_id)
        for renderable, entity, location in sorted(self.ecs.join(renderables, entities, locations)):
            if not location.position in coverage:
                # Not inside area covered by camera, skip!
                continue

            tile = None
            position = location.position.offset(coverage)
            if visible[position]:
                # Visible by player
                tile = renderable.tile_visible
            elif renderable.render_order == RenderOrder.PROPS and revealed[position]:
                # Not visible, but revealed
                tile = renderable.tile_revealed
            # TODO: Some components checks like entity.has(components.Hidden)

            if tile is not None:
                render_position = location.position.offset(self.position)
                if not tile.ch:
                    self.panel.paint(tile.colors, render_position)
                else:
                    self.panel.draw(tile, render_position)

    def render(self, actor=None, location=None):
        position = None
        fov = None
        seen = None
        actor = actor or self.ecs.resources.current_player
        if actor:
            locations = self.ecs.manage(components.Location)
            viewsheds = self.ecs.manage(components.Viewshed)
            location = locations.get(actor)
            fov = viewsheds.get(actor).fov
        if location:
            position = location.position
        level = self.spatial.get_level(location.level_id)

        if fov is None:
            fov = np.ones(level.size, dtype=np.bool)

        level_memories = self.ecs.manage(components.LevelMemory)
        memory = level_memories.get(actor)
        if memory:
            seen = memory.revealed.get(location.level_id)
        else:
            seen = self.spatial.revealable(location.level_id)

        self.calc_position(level, position)

        coverage = self.get_coverage(level)
        if not coverage:
            # Nothing to display, nothing to do here...
            return

        # Calculate visibility masks
        revealed = self.get_covered(seen, coverage)
        visible = self.get_covered(fov, coverage)

        terrain = self.get_covered(level.terrain, coverage)

        with perf.Perf(self.draw_boundaries):
            self.draw_boundaries(level.size)
        with perf.Perf(self.draw_terrain):
            self.draw_terrain(location.level_id, terrain, coverage, revealed, visible)
        with perf.Perf(self.draw_entities):
            self.draw_entities(location.level_id, coverage, revealed, visible)


class MessageLog(toolkit.Renderer):

    def render(self):
        """Render logging records."""
        for offset, msg in enumerate(reversed(logs.LOGS_HISTORY), start=1):
            if offset > self.panel.height:
                break
            self.panel.print(
                msg.message,
                Position(0, self.panel.height-offset),
                colors=Colors(fg=msg.fg),
            )

