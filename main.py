#!/usr/bin/env python3

import logging

import logs

from geometry import Size
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


log = logging.getLogger('rogal.main')


CONSOLE_SIZE = Size(80, 50)



def render(wrapper, root_panel, ecs, level):
    root_panel.clear()

    # Rendering terrain
    game_map.render(level, root_panel)

    # Render all renderable entities
    locations = ecs.manage(components.Location)
    renderables = ecs.manage(components.Renderable)
    for renderable, location in sorted(ecs.join(renderables, locations)):
        root_panel.draw(renderable.tile, location.position)

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
        render(wrapper, root_panel, ecs, level)

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

        level = game_map.generate(root_panel.size*0.75)
        player = entities.create_player(ecs)
        entities.spawn(ecs, player, level, root_panel.center)

        loop(wrapper, root_panel, ecs, level, player)


if __name__ == "__main__":
    logs.setup()

    main()

