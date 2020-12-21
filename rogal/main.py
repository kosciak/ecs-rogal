import logging
import time

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

from . import ai
from .player import try_move

import tcod


log = logging.getLogger('rogal.main')


PALETTE = TANGO_DARK

CONSOLE_SIZE = Size(80, 50)

CAMERA_SIZE = Size(12, 12)
LEVEL_SIZE = Size(20,20)


def render(wrapper, root_panel, ecs, level, player):
    print(f'Render @ {time.time()}')
    root_panel.clear()
    camera, message_log = root_panel.split(bottom=12)
    #camera = root_panel.create_panel(Position(10,10), CAMERA_SIZE)

    render_message_log(message_log.framed('logs'))

    render_camera(camera.framed('mapcam'), ecs, level, player)

    # Show rendered panel
    wrapper.flush(root_panel)


def handle_events(wrapper, ecs, level, player):
    #for event in wrapper.events(wait=1/30):
    for event in wrapper.events():
        # Just print all events, and gracefully quit on closing window
        print(f'Event: {event}')

        # TODO: implement tcod.EventDispatch
        if event.type == 'KEYDOWN':
            key = event.sym
            if key == keys.ESCAPE_KEY:
                log.warning('Quitting...')
                raise SystemExit()

            if key in keys.WAIT_KEYS:
                log.info('Waiting...')
                return True

            direction = keys.MOVE_KEYS.get(key)
            if direction:
                return try_move(ecs, level, player, direction)

        if event.type == 'QUIT':
            log.warning('Quitting...')
            raise SystemExit()


def loop(wrapper, root_panel, ecs, level, player):
    actors = ecs.manage(components.Actor)
    locations = ecs.manage(components.Location)
    movement = ecs.manage(components.WantsToMove)

    while True:
        for entity, actor, location in ecs.join(ecs.entities, actors, locations):
            # Run systems
            ecs.systems_run()

            if entity == player:
                # Handle user input until action is performed
                action_performed = False
                while not action_performed:
                    render(wrapper, root_panel, ecs, level, player)
                    action_performed = handle_events(wrapper, ecs, level, player)
            else:
                # Monster move
                direction = ai.random_move(level, location.position)
                movement.insert(entity, direction)


def run():
    ecs = ECS()

    # Register systems
    ecs.register(systems.particle_system_run)
    ecs.register(systems.melee_system_run)
    ecs.register(systems.movement_system_run)
    ecs.register(systems.map_indexing_system_run)
    ecs.register(systems.visibility_system_run)

    entities.create_all_terrains(ecs)

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
        ecs.add_level(level)

        player = entities.create_player(ecs)
        #entities.spawn(ecs, player, level, level.center)
        entities.spawn(ecs, player, level.id, Position(3,3))
        for offset in [(-2,-2), (2,2), (-3,3), (3,-3)]:
            monster = entities.create_monster(ecs)
            position = level.center + Position(*offset)
            entities.spawn(ecs, monster, level.id, position)

        loop(wrapper, root_panel, ecs, level, player)

