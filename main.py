#!/usr/bin/env python3

import logging

import logs

from geometry import Position, Size
from colors.x11 import Color, TANGO_DARK
from tilesets import TERMINAL_12x12_CP

from wrappers import TcodWrapper
import keys

import game_map

from ecs import ECS
import components
import entities
import systems

import tcod


logs.setup()
log = logging.getLogger('rogal.main')


CONSOLE_SIZE = Size(80, 50)

SCROLLABLE_CAMERA = True

CAMERA_SIZE = Size(12, 12)
LEVEL_SIZE = Size(14,9)


def render_message_log(panel):
    from renderable import Colors
    for offset, msg in enumerate(reversed(logs.LOGS_HISTORY), start=1):
        if offset > panel.height:
            break
        panel.print(msg.message, Position(0, panel.height-offset), colors=Colors(fg=msg.fg))


def render_camera(panel, ecs, level, player, scrollable=SCROLLABLE_CAMERA):
    """Render level contets viewed through (scrollable) camera."""
    import numpy as np
    from geometry import Position, Rectangle
    import tiles

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


def render(wrapper, root_panel, ecs, level, player):
    root_panel.clear()
    camera, message_log = root_panel.split(bottom=7)
    #camera = root_panel.create_panel(Position(10,10), CAMERA_SIZE)

    render_message_log(message_log.framed('logs'))

    render_camera(camera.framed('mapcam'), ecs, level, player)

    # Show rendered panel
    wrapper.flush(root_panel)


def handle_events(wrapper, ecs, level, player):
    for event in wrapper.events():
        # Just print all events, and gracefully quit on closing window
        #log.debug('Event: %s', event)

        # TODO: implement tcod.EventDispatch
        if event.type == 'KEYDOWN':
            key = event.sym
            if key == keys.ESCAPE_KEY:
                log.warning('Quitting...')
                raise SystemExit()

            direction = keys.MOVE_KEYS.get(key)
            if direction:
                log.info('Move: %s', direction)
                movements = ecs.manage(components.WantsToMove)
                movements.insert(player, components.WantsToMove(direction))

        if event.type == 'QUIT':
            log.warning('Quitting...')
            raise SystemExit()


def loop(wrapper, root_panel, ecs, level, player):
    while True:
        # Render
        # TODO: No need to render after EVERY single event!
        render(wrapper, root_panel, ecs, level, player)

        # Handle user input
        handle_events(wrapper, ecs, level, player)

        # Run systems
        # Apply movements
        systems.movement_system_run(ecs, level)


def main():
    ecs = ECS()

    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=TANGO_DARK,
        tileset=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    with wrapper as wrapper:
        root_panel = wrapper.create_panel()

        #level = game_map.generate(root_panel.size*0.75)
        #level = game_map.generate(root_panel.size*1.025)
        level = game_map.generate(LEVEL_SIZE)
        player = entities.create_player(ecs)
        entities.spawn(ecs, player, level, level.center)
        for offset in [(-2,-2), (2,2), (-3,3), (3,-3)]:
            monster = entities.create_monster(ecs)
            position = level.center + Position(*offset)
            entities.spawn(ecs, monster, level, position)

        loop(wrapper, root_panel, ecs, level, player)


if __name__ == "__main__":
    main()

