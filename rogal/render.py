import numpy as np

from . import logs

from . import components
from .geometry import Position, Size, Rectangle
from .renderable import Colors
from .tiles import TermTiles as tiles


"""Rendering components."""


SCROLLABLE_CAMERA = True
#SCROLLABLE_CAMERA = False

SHOW_BOUNDARIES = True


def render_message_log(panel):
    """Render logging records."""
    for offset, msg in enumerate(reversed(logs.LOGS_HISTORY), start=1):
        if offset > panel.height:
            break
        panel.print(msg.message, Position(0, panel.height-offset), colors=Colors(fg=msg.fg))


def render_camera(panel, ecs, level, player, 
        scrollable=SCROLLABLE_CAMERA, 
        show_boundaries=SHOW_BOUNDARIES):
    """Render level contets viewed through (scrollable) camera."""

    player_position = player.get(components.Location).position

    # Select what camera should be centered on
    if scrollable:
        # Player position, relative to level
        cam_center = player_position
    else:
        # Level center
        cam_center = level.center

    # Camera, position relative to level
    camera = Rectangle(
        Position(cam_center.x-panel.width//2, cam_center.y-panel.height//2),
        panel.size
    )
    # For level-centered camera need to move camera if level.size > camera.size and approaching edge
    # Adjust top-left corner
    adjusted_position = Position(
        min(camera.x, player_position.x-1),
        min(camera.y, player_position.y-1)
    )
    # Adjust bottom-right corner
    adjust_move = Position(
       max(0, 2+player_position.x-camera.x2),
       max(0, 2+player_position.y-camera.y2), 
    )
    camera.position = adjusted_position+adjust_move

    # Draw BOUNDARIES of the map/level
    if show_boundaries:
        boundaries = set()
        for boundary in [
            Rectangle(Position(-1,-1), Size(level.width+2, 1)),
            Rectangle(Position(-1,level.height), Size(level.width+2, 1)),
            Rectangle(Position(-1, 0), Size(1, level.height)),
            Rectangle(Position(level.width, 0), Size(1, level.height)),
        ]:
            intersection = boundary & camera
            if intersection:
                boundaries.update(intersection.positions)
        for position in boundaries:
            panel.draw(tiles.BOUNDARY.tile, position.offset(camera.position))

    # Part of level that is covered by camera
    cam_coverage = camera & level
    if not cam_coverage:
        # Nothing to display, nothing to do here...
        return

    # Slice level.terrain to get part that is covered by camera
    terrain = level.terrain[
        cam_coverage.x : cam_coverage.x2,
        cam_coverage.y : cam_coverage.y2
    ]

    # Visibility info
    revealed = level.revealed[
        cam_coverage.x : cam_coverage.x2,
        cam_coverage.y : cam_coverage.y2
    ]
    visible = level.visible[
        cam_coverage.x : cam_coverage.x2,
        cam_coverage.y : cam_coverage.y2
    ]
    revealed_not_visible = revealed ^ visible

    # Offset for drawing a terrain tile with a mask
    # It's mirrored camera.position but only with x,y values > 0
    mask_offset = Position(max(0, camera.x*-1), max(0, camera.y*-1))

    # Draw TERRAIN tiles
    renderables = ecs.manage(components.Renderable)
    for terrain_id in np.unique(terrain):
        if not terrain_id:
            continue
        terrain_mask = terrain == terrain_id
        renderable = renderables.get(ecs.get(terrain_id))
        # Visible
        mask = terrain_mask & visible
        if np.any(mask):
            tile = renderable.tile_visible
            panel.mask(tile, mask, mask_offset)
        # Revealed but not visible
        mask = terrain_mask & revealed_not_visible
        if np.any(mask):
            tile = renderable.tile_revealed
            panel.mask(tile, mask, mask_offset)

    # Draw all renderable ENTITIES, in order described by Renderable.render_order
    locations = ecs.manage(components.Location)
    for renderable, location in sorted(ecs.join(renderables, locations)):
        if not location.level_id == level.id:
            # Not on the map/level we are rendering, skip!
            continue
        if not location.position in cam_coverage:
            # Not inside area covered by camera, skip!
            continue
        if not level.revealed[location.position]:
            # Not yet revealed, skip!
            continue
        if not level.visible[location.position]:
            # Not visible, skip!
            # TODO: What about doors, staircases ang others which placement should be remembered?
            continue
        # TODO: Some components checks like entity.has(components.Hidden)
        render_position = location.position.offset(camera.position)
        tile = renderable.tile_visible
        if not tile.ch:
            panel.paint(tile.colors, render_position)
        else:
            panel.draw(tile, render_position)

