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
import ecs
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

    entities = ecs.EntitiesManager()
    location_manager = entities.manage(components.Location)
    move_manager = entities.manage(components.WantsToMove)

    player = entities.create(
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
            # TODO: No need to have entity, just (direction, location)
            for entity, direction, location in move_manager.join(location_manager):
                log.debug(f'Moving {entity} in {direction}')
                location.position = location.position.move(direction)
            move_manager.clear()

            # Rendering
            root_panel.clear()
            game_map.render(level, root_panel)
            # TODO: Something like: location_manager.filter(components.Renderable)
            # TODO: No need to have entity, just (location, renderable)
            for entity, location, renderable in entities.filter(components.Location, components.Renderable):
                root_panel.draw(renderable.tile, location.position)
            wrapper.flush(root_panel)

            for event in wrapper.events():
                # Just print all events, and gracefully quit on closing window
                log.debug('Event: %s', event)
                if event.type == 'KEYDOWN':
                    key = event.sym
                    if key == keys.ESCAPE_KEY:
                        log.warning('Quitting...')
                        raise SystemExit()

                    direction = keys.MOVE_KEYS.get(key)
                    if direction:
                        log.info('Move: %s', direction)
                        move_manager.insert(player, components.WantsToMove(direction))

                if event.type == 'QUIT':
                    log.warning('Quitting...')
                    raise SystemExit()


if __name__ == "__main__":
    logs.setup()

    main()
