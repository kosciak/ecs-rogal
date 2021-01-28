import logging
import time

import numpy as np

from . import logs

from . import bitmask
from . import components
from .geometry import Rectangular, Position, Size, Rectangle
from .renderable import RenderOrder, Colors, Tile
from . import terrain

from .utils import perf


log = logging.getLogger(__name__)


"""Rendering components."""


SCROLLABLE_CAMERA = True
SCROLLABLE_CAMERA = False

SHOW_BOUNDARIES = True

BITMASK_TERRAIN_TYPE = terrain.Type.WALL
BITMASKED_WALLS = bitmask.WALLS_DLINE


class Renderer:

    def __init__(self, ecs, spatial, wrapper, panel, tileset):
        self.ecs = ecs
        self.spatial = spatial

        self.wrapper = wrapper
        self.panel = panel
        self.tileset = tileset

    def render(self, actor):
        if not actor:
            return False
        self.panel.clear()
        camera, message_log = self.panel.split(bottom=12)
        #camera = root_panel.create_panel(Position(10,10), CAMERA_SIZE)

        render_message_log(message_log.framed('logs'))

        cam = Camera(self.ecs, self.spatial, camera.framed('mapcam'), self.tileset)
        cam.render(actor=actor)

        # Show rendered panel
        self.wrapper.flush(self.panel)
        return True


class Camera(Rectangular):

    def __init__(self, ecs, spatial, panel, tileset,
                 scrollable=SCROLLABLE_CAMERA, show_boundaries=SHOW_BOUNDARIES):
        self.ecs = ecs
        self.spatial = spatial

        self.panel = panel
        self.tileset = tileset

        self.position = Position.ZERO
        self.size = self.panel.size

        self.scrollable = scrollable
        self.show_boundaries = show_boundaries

    def set_center(self, level, position=None):
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

    def get_revealed(self, seen, coverage):
        """Return visible masks."""
        revealed = seen[
            coverage.x : coverage.x2,
            coverage.y : coverage.y2
        ]
        return revealed

    def get_visible(self, fov, coverage):
        """Return revealed masks."""
        visible = fov[
            coverage.x : coverage.x2,
            coverage.y : coverage.y2
        ]
        return visible

    def walls_bitmask(self, level_id, revealed, terrain_type):
        walls_mask = self.spatial.terrain_type(level_id, terrain_type)
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
            ch = BITMASKED_WALLS[bitmask_value]
            mask = terrain_mask & (walls_mask == bitmask_value)
            self.draw_terrain_tile(
                mask, visible, revealed, mask_offset,
                renderable, ch,
            )

    def draw_terrain(self, level_id, terrain, coverage, revealed, visible):
        """Draw TERRAIN tiles."""
        # Slice terrain to get part that is covered by camera
        covered_terrain = terrain[
            coverage.x : coverage.x2,
            coverage.y : coverage.y2
        ]

        # Bitshift masking for terrain.Type.WALL terrain
        walls_mask = self.walls_bitmask(level_id, revealed, BITMASK_TERRAIN_TYPE)[
            coverage.x : coverage.x2,
            coverage.y : coverage.y2
        ]

        # Offset for drawing a terrain tile with a mask
        # It's mirrored camera.position but only with x,y values > 0
        mask_offset = Position(max(0, self.x*-1), max(0, self.y*-1))

        revealed_not_visible = revealed ^ visible

        renderables = self.ecs.manage(components.Renderable)
        for terrain_id in np.unique(covered_terrain):
            if not terrain_id:
                continue

            terrain_mask = covered_terrain == terrain_id
            renderable = renderables.get(terrain_id)
            if not renderable:
                continue

            if terrain_id >> 4 == BITMASK_TERRAIN_TYPE:
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
            if visible[location.position]:
                # Visible by player
                tile = renderable.tile_visible
            elif revealed[location.position]:
                # Not visible, but revealed
                if renderable.render_order == RenderOrder.PROPS:
                    tile = renderable.tile_revealed
            # TODO: Some components checks like entity.has(components.Hidden)

            if tile is not None:
                render_position = location.position.offset(self.position)
                if not tile.ch:
                    self.panel.paint(tile.colors, render_position)
                else:
                    self.panel.draw(tile, render_position)

    def render(self, actor=None, location=None, level=None):
        position = None
        fov = None
        seen = None
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

        self.set_center(level, position)

        coverage = self.get_coverage(level)
        if not coverage:
            # Nothing to display, nothing to do here...
            return

        # Calculate visibility masks
        revealed = self.get_revealed(seen, coverage)
        visible = self.get_visible(fov, coverage)

        self.draw_boundaries(level.size)
        self.draw_terrain(location.level_id, level.terrain, coverage, revealed, visible)
        self.draw_entities(location.level_id, coverage, revealed, visible)


def render_message_log(panel):
    """Render logging records."""
    for offset, msg in enumerate(reversed(logs.LOGS_HISTORY), start=1):
        if offset > panel.height:
            break
        panel.print(msg.message, Position(0, panel.height-offset), colors=Colors(fg=msg.fg))

