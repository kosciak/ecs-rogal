import logging
from operator import itemgetter

import numpy as np

from . import logs

from .data import Bitmasks
from .bitmask import bitmask_walls
from . import components
from .geometry import Position, WithPositionMixin, Size
from .geometry.rectangle import Rectangle
from .console.core import Colors
from .tiles import RenderOrder, Tile
from . import terrain

from .ui_toolkit import core

from .utils import perf


log = logging.getLogger(__name__)


"""Rendering components."""


CAMERA_SIZE = Size(15, 15)
CAMERA_SIZE = Size(26, 26)

SCROLLABLE_CAMERA = True
SCROLLABLE_CAMERA = False

SHOW_BOUNDARIES = True


class Camera(WithPositionMixin, core.Renderer, core.UIElement):

    def __init__(self, ecs,
                 scrollable=SCROLLABLE_CAMERA, show_boundaries=SHOW_BOUNDARIES):
        super().__init__()
        self.ecs = ecs
        self.spatial = self.ecs.resources.spatial

        self.tileset = self.ecs.resources.tileset

        self.cam_area = None

        self.scrollable = scrollable
        self.show_boundaries = show_boundaries

        self.walls_terrain_type = terrain.Type.WALL
        # self.bitmasked_walls = Bitmasks.WALLS_DLINE
        self.bitmasked_walls = Bitmasks.WALLS_WLINE_ENDS

    @property
    def position(self):
        return self.cam_area.position

    def camera_position(self, panel, level, position=None):
        """Select what camera should be centered on."""
        if not position or not self.scrollable:
            # Use center of given level
            position = level.center
        camera_position = Position(
            position.x-panel.width//2,
            position.y-panel.height//2
        )

        # For level-centered camera need to move camera if level.size > camera.size and approaching edge
        # TODO: Test it, and... 
        # TODO: Maybe use viewshed.view_range for adjustments? Whole viewshed should be rendered
        # Adjust top-left corner
        adjusted_position = Position(
            min(camera_position.x, position.x-1),
            min(camera_position.y, position.y-1)
        )
        # Adjust bottom-right corner
        adjust_move = Position(
            max(0, 2+position.x-(camera_position.x+panel.width)),
            max(0, 2+position.y-(camera_position.y+panel.height)),
        )

        return adjusted_position + adjust_move

    def update_cam_area(self, panel, level, position):
        position = self.camera_position(panel, level, position)
        self.cam_area = Rectangle(position, panel.size)

    def get_coverage(self, panel, level):
        """Return part of the level that is covered by camera."""
        coverage = self.cam_area & level
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
        return bitmask_walls(walls_mask, revealed)

    def draw_boundaries(self, panel, level_size):
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
            intersection = self.cam_area & boundary
            if intersection:
                boundaries.update(intersection.positions)
        for position in boundaries:
            tile = self.tileset.get('BOUNDARY').visible
            render_position = position.offset(self.position)
            panel.draw(tile,glyph, tile.colors, render_position)

    def draw_terrain_tile(self,
        panel,
        terrain_mask, visible, revealed, mask_offset,
        renderable, ch=None,
    ):
        # Visible
        mask = terrain_mask & visible
        if np.any(mask):
            tile = renderable.tile_visible
            if ch is not None:
                tile = Tile.create(ch, tile.fg, tile.bg)
            panel.mask(tile.glyph, tile.colors, mask, mask_offset)

        # Revealed but not visible
        mask = terrain_mask & revealed
        if np.any(mask):
            tile = renderable.tile_revealed
            if ch is not None:
                tile = Tile.create(ch, tile.fg, tile.bg)
            panel.mask(tile.glyph, tile.colors, mask, mask_offset)

    def draw_bitmasked_terrain_tile(self,
        panel,
        walls_mask, terrain_mask, visible, revealed, mask_offset,
        renderable,
    ):
        for bitmask_value in np.unique(walls_mask):
            ch = self.bitmasked_walls[bitmask_value]
            mask = terrain_mask & (walls_mask == bitmask_value)
            self.draw_terrain_tile(
                panel,
                mask, visible, revealed, mask_offset,
                renderable, ch,
            )

    def draw_terrain(self, panel, level_id, terrain, coverage, revealed, visible):
        """Draw TERRAIN tiles."""

        # Bitshift masking for terrain.Type.WALL terrain
        walls_mask = self.walls_bitmask(level_id, coverage, revealed, self.walls_terrain_type)

        # Offset for drawing a terrain tile with a mask
        # It's mirrored camera.position but only with x,y values > 0
        mask_offset = Position(
            max(0, self.x*-1),
            max(0, self.y*-1)
        )

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
                    panel,
                    walls_mask,
                    terrain_mask, visible, revealed_not_visible, mask_offset,
                    renderable,
                )
            else:
                self.draw_terrain_tile(
                    panel,
                    terrain_mask, visible, revealed_not_visible, mask_offset,
                    renderable,
                )

    def draw_entities(self, panel, level_id, coverage, revealed, visible):
        """Draw all renderable ENTITIES, in order described by Renderable.render_order."""
        renderables = self.ecs.manage(components.Renderable)
        locations = self.ecs.manage(components.Location)

        entities = self.spatial.entities(level_id)
        for renderable, entity, location in sorted(
            self.ecs.join(renderables, entities, locations),
            key=itemgetter(0)
        ):
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
                    panel.paint(tile.colors, render_position)
                else:
                    panel.draw(tile.glyph, tile.colors, render_position)

    def get_seen(self, actor, location):
        level_memories = self.ecs.manage(components.LevelMemory)
        memory = level_memories.get(actor)
        if memory:
            seen = memory.revealed.get(location.level_id)
        else:
            seen = self.spatial.revealable(location.level_id)
        return seen

    def render(self, panel, timestamp, actor=None, location=None):
        fov = None
        actor = actor or self.ecs.resources.current_player
        if actor:
            locations = self.ecs.manage(components.Location)
            viewsheds = self.ecs.manage(components.Viewshed)
            location = locations.get(actor)
            fov = viewsheds.get(actor).fov
        if not location:
            return
        position = location.position
        level = self.spatial.get_level(location.level_id)

        if fov is None:
            fov = np.ones(level.size, dtype=np.bool)

        seen = self.get_seen(actor, location)

        self.update_cam_area(panel, level, position)

        coverage = self.get_coverage(panel, level)
        if not coverage:
            # Nothing to display, nothing to do here...
            return

        # Calculate visibility masks
        revealed = self.get_covered(seen, coverage)
        visible = self.get_covered(fov, coverage)

        terrain = self.get_covered(level.terrain, coverage)

        with perf.Perf(self.draw_boundaries):
            self.draw_boundaries(panel, level.size)
        with perf.Perf(self.draw_terrain):
            self.draw_terrain(panel, location.level_id, terrain, coverage, revealed, visible)
        with perf.Perf(self.draw_entities):
            self.draw_entities(panel, location.level_id, coverage, revealed, visible)


class MessageLog(core.Renderer, core.UIElement):

    def render(self, panel, timestamp):
        """Render logging records."""
        for offset, msg in enumerate(reversed(logs.LOGS_HISTORY), start=1):
            if offset > panel.height:
                break
            panel.print(
                msg.message,
                Position(0, panel.height-offset),
                colors=Colors(fg=msg.fg),
            )

