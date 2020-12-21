import logging

from .geometry import Position, Size
from .colors.x11 import Color, TANGO_DARK, TANGO_LIGHT
from .tilesheets import TERMINAL_12x12_CP

from .wrappers import TcodWrapper
from . import keys

from . import game_map

from .ecs import ECS
from . import components
from . import entities
from . import systems

from .render import render_message_log, render_camera

import tcod


log = logging.getLogger('rogal.main')


PALETTE = TANGO_DARK

CONSOLE_SIZE = Size(80, 50)

CAMERA_SIZE = Size(12, 12)
LEVEL_SIZE = Size(20,20)


def render(wrapper, root_panel, ecs, level, player):
    root_panel.clear()
    camera, message_log = root_panel.split(bottom=7)
    #camera = root_panel.create_panel(Position(10,10), CAMERA_SIZE)

    render_message_log(message_log.framed('logs'))

    render_camera(camera.framed('mapcam'), ecs, level, player)

    # Show rendered panel
    wrapper.flush(root_panel)


def try_move(ecs, level, player, direction):
    location = player.get(components.Location)
    exits = level.get_exits(location.position)
    if direction in exits:
        log.info(f'Move: {direction}')
        movements = ecs.manage(components.WantsToMove)
        movements.insert(player, components.WantsToMove(direction))
    else:
        log.warning(f'{direction} blocked!')


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
                try_move(ecs, level, player, direction)

        if event.type == 'QUIT':
            log.warning('Quitting...')
            raise SystemExit()


def loop(wrapper, root_panel, ecs, world, level, player):
    while True:
        # Run systems
        ecs.systems_run(world)

        # Render
        # TODO: No need to render after EVERY single event!
        render(wrapper, root_panel, ecs, level, player)

        # Handle user input
        handle_events(wrapper, ecs, level, player)


def run():
    ecs = ECS()

    # Register systems
    ecs.register(systems.movement_system_run)
    ecs.register(systems.map_indexing_system_run)
    ecs.register(systems.visibility_system_run)

    entities.create_terrain(ecs)

    world = {}

    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=PALETTE,
        tilesheet=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    with wrapper as wrapper:
        root_panel = wrapper.create_panel()

        #level = game_map.generate(root_panel.size*0.75)
        #level = game_map.generate(root_panel.size*1.025)
        level = game_map.generate(LEVEL_SIZE)
        world[level.id] = level

        player = entities.create_player(ecs)
        #entities.spawn(ecs, player, level, level.center)
        entities.spawn(ecs, player, level, Position(3,3))
        for offset in [(-2,-2), (2,2), (-3,3), (3,-3)]:
            monster = entities.create_monster(ecs)
            position = level.center + Position(*offset)
            entities.spawn(ecs, monster, level, position)

        loop(wrapper, root_panel, ecs, world, level, player)

