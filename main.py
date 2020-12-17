#!/usr/bin/env python3

import logging

import logs
from geometry import Size
from colors.x11 import Color, TANGO_DARK
from tilesets import TERMINAL_12x12_CP
from wrappers import TcodWrapper
import keys
import game_map
from renderable import Tile, RenderOrder
from ecs import ECS
import components

import tcod


log = logging.getLogger('rogal.main')


CONSOLE_SIZE = Size(80, 50)


def main():
    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=TANGO_DARK,
        tileset=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    ecs = ECS()
    location_manager = ecs.manage(components.Location)
    movement_manager = ecs.manage(components.WantsToMove)

    player = ecs.create(
        components.Player(),
        components.Renderable(Tile.create('@', fg=15), RenderOrder.ACTORS),
        components.Viewshed(view_range=8),
    )

    with wrapper as wrapper:
        root_panel = wrapper.create_panel()
        level = game_map.generate(root_panel.size*0.75)

        location = components.Location(level.id, root_panel.center)
        location_manager.insert(player, location)

        while True:
            # Movement system
            for location, direction in ecs.join(location_manager, movement_manager):
                location.position = location.position.move(direction)
                # TODO: Add some HasMoved to flag to entity?
            movement_manager.clear()

            # Rendering
            root_panel.clear()
            game_map.render(level, root_panel)
            # TODO: Something like: location_manager.filter(components.Renderable)
            for location, renderable in ecs.join(location_manager, ecs.manage(components.Renderable)):
                root_panel.draw(renderable.tile, location.position)
            wrapper.flush(root_panel)

            for event in wrapper.events():
                # Just print all events, and gracefully quit on closing window
                #log.debug('Event: %s', event)
                if event.type == 'KEYDOWN':
                    key = event.sym
                    if key == keys.ESCAPE_KEY:
                        log.warning('Quitting...')
                        raise SystemExit()

                    direction = keys.MOVE_KEYS.get(key)
                    if direction:
                        log.info('Move: %s', direction)
                        movement_manager.insert(player, components.WantsToMove(direction))

                if event.type == 'QUIT':
                    log.warning('Quitting...')
                    raise SystemExit()


if __name__ == "__main__":
    logs.setup()

    main()
