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

CAMERA_SIZE = Size(10, 10)
LEVEL_SIZE = Size(12,8)


def render_message_log(panel):
    from renderable import Colors
    for offset, msg in enumerate(reversed(logs.LOGS_HISTORY), start=1):
        if offset > panel.height:
            break
        panel.print(msg.message, Position(1, panel.height-offset), colors=Colors(fg=msg.fg))


def render_camera(panel, ecs, level, player):
    import numpy as np
    from terrain import Terrain
    from geometry import Position, Rectangle
    import tiles

    player_position = ecs.manage(components.Location).get(player).position

    tiles = {
        Terrain.STONE_WALL.id:     tiles.STONE_WALL,
        Terrain.STONE_FLOOR.id:    tiles.STONE_FLOOR,
    }

    log.debug('--- Rendering level ---')
    log.debug(f'Panel           : {panel}')
    log.debug(f'Level           : {level.size}')
    centers_offset = panel.center - level.center
    render_offset = Position(
        min((panel.width-level.width)/2, centers_offset.x),
        min((panel.height-level.height)/2, centers_offset.y),
    )
    log.debug(f'Render offset   : {render_offset}')

    level_rectangle = Rectangle(panel.position+render_offset, level.size)
    log.debug(f'Level rect      : {level_rectangle}')
    #intersection = panel & level_rectangle
    intersection = level_rectangle & panel
    log.debug(f'Intersection    : {intersection}')

    # Render terrain
    slice_x = slice(abs(min(0, render_offset.x)), min(level.width, level.width+render_offset.x))
    slice_y = slice(abs(min(0, render_offset.y)), min(level.height, level.height+render_offset.y))
    print('???', slice_x, slice_y)
    terrain = level.terrain[slice_x, slice_y]
    print('???', terrain.shape)
    mask_offset = Position(max(0, render_offset.x), max(0, render_offset.y))
    for tile_id in np.unique(terrain):
        mask = terrain == tile_id
        tile = tiles.get(tile_id)
        panel.mask(tile, mask, mask_offset)

    # Render all renderable entities
    locations = ecs.manage(components.Location)
    renderables = ecs.manage(components.Renderable)
    for renderable, location in sorted(ecs.join(renderables, locations)):
        render_position = render_offset + location.position
        if not panel.position+render_position in panel:
            continue
        panel.draw(renderable.tile, render_position)


def render(wrapper, root_panel, ecs, level, player):
    root_panel.clear()
    camera, message_log = root_panel.split(bottom=5)
    camera_position = Position(camera.center.x-CAMERA_SIZE.width/2, camera.center.y-CAMERA_SIZE.height/2)
    camera = root_panel.create_panel(camera_position, CAMERA_SIZE)

    render_message_log(message_log)

    render_camera(camera, ecs, level, player)
    root_panel._draw_frame(camera.x-1, camera.y-1, camera.width+2, camera.height+2, 'mapcam', clear=False)

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

        loop(wrapper, root_panel, ecs, level, player)


if __name__ == "__main__":
    main()

