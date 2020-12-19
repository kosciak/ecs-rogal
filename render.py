import logs

import components
from geometry import Position, Size, Rectangle
from renderable import Colors
import tiles

import numpy as np


"""Rendering components."""


SCROLLABLE_CAMERA = True

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

    # Select what camera should be centered on
    if scrollable:
        # Player position, relative to level
        cam_center = player.get(components.Location).position
    else:
        # Level center
        cam_center = level.center

    # Camera, position relative to level
    camera = Rectangle(
        Position(cam_center.x-panel.width//2, cam_center.y-panel.height//2),
        panel.size
    )

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
            panel.draw(tiles.BOUNDARY, position.offset(camera.position))

    # Part of level that is covered by camera
    cam_coverage = camera & Rectangle(Position.ZERO, level.size)
    if not cam_coverage:
        # Nothing to display, nothing to do here...
        return

    # TODO: Handle level.visible, level.revealed flags

    # Slice level.terrain to get part that is covered by camera
    terrain = level.terrain[cam_coverage.x:cam_coverage.x2, cam_coverage.y:cam_coverage.y2]

    # Offset for drawing a terrain tile with a mask
    # It's mirrored camera.position but only with x,y values > 0
    mask_offset = Position(max(0, camera.x*-1), max(0, camera.y*-1))

    # Draw TERRAIN tiles
    for terrain_id in np.unique(terrain):
        mask = terrain == terrain_id
        tile = tiles.TERRAIN.get(terrain_id)
        panel.mask(tile, mask, mask_offset)

    # Draw all renderable ENTITIES, in order described by Renderable.render_order
    locations = ecs.manage(components.Location)
    renderables = ecs.manage(components.Renderable)
    for renderable, location in sorted(ecs.join(renderables, locations)):
        if not location.map_id == level.id:
            # Not on the map/level we are rendering, skip!
            continue
        if not location.position in cam_coverage:
            # Not inside area covered by camera, skip!
            continue
        render_position = location.position.offset(camera.position)
        panel.draw(renderable.tile, render_position)


