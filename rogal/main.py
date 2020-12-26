import logging
import time

import tcod

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

from .run_state import RunState

from .render import render_message_log, render_camera

from . import ai
from .player import try_move


log = logging.getLogger(__name__)


PALETTE = TANGO_DARK

CONSOLE_SIZE = Size(80, 50)

CAMERA_SIZE = Size(15, 15)
LEVEL_SIZE = Size(21,21)


def render(wrapper, root_panel, ecs, level, player):
    if not level or not player:
        return
    log.debug(f'Render @ {time.time()}')
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
        log.debug(f'Event: {event}')

        # TODO: implement tcod.EventDispatch
        if event.type == 'KEYDOWN':
            key = event.sym
            if key == keys.ESCAPE_KEY:
                log.warning('Quitting...')
                raise SystemExit()

            if key in keys.WAIT_KEYS:
                log.info('Waiting...')
                return 60

            direction = keys.MOVE_KEYS.get(key)
            if direction:
                return try_move(ecs, level, player, direction)

        if event.type == 'QUIT':
            log.warning('Quitting...')
            raise SystemExit()


def loop(wrapper, root_panel, ecs):
    acts_now = ecs.manage(components.ActsNow)
    players = ecs.manage(components.Player)
    locations = ecs.manage(components.Location)
    waiting = ecs.manage(components.WaitsForAction)

    pending_animations = ecs.manage(components.Animation)

    player = None
    level = None

    # Preparation
    ecs.run(RunState.PRE_RUN)

    while True:
        # Run clocks
        ecs.run(RunState.TICKING)

        for actor, location in ecs.join(acts_now.entities, locations):
            # Each actor performs action

            if actor in players:
                player = actor
                # Handle user input until action is performed
                action_cost = 0
                while not action_cost:
                    ecs.run(RunState.WAITING_FOR_INPUT)
                    level = ecs.levels.get(location.level_id)
                    render(wrapper, root_panel, ecs, level, actor)
                    action_cost = handle_events(wrapper, ecs, level, actor)

            else:
                # Actor AI move
                action_cost = ai.perform_action(ecs, actor)

            # Action performed
            ecs.run(RunState.ACTION_PERFORMED)
            waiting.insert(actor, action_cost)

            # Render real time animated effects
            while len(pending_animations):
                ecs.run(RunState.ANIMATIONS)
                render(wrapper, root_panel, ecs, level, player)
                time.sleep(1/60)


def run():
    # ECS initialization
    ecs = ECS()

    # Register systems
    # NOTE: Systems are run in order they were registered
    ecs.register(systems.ParticlesSystem())

    ecs.register(systems.ActionsQueueSystem())

    ecs.register(systems.MeleeCombatSystem())
    ecs.register(systems.MovementSystem())
    ecs.register(systems.OperateSystem())

    ecs.register(systems.MapIndexingSystem())
    ecs.register(systems.VisibilitySystem())

    # Entities initialization
    for entity_id, template in entities.ALL_TERRAIN:
        entities.create(ecs, template, entity_id=entity_id)

    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=PALETTE,
        tilesheet=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    with wrapper as wrapper:
        root_panel = wrapper.create_panel()

        # Level(s) generation
        #level = game_map.generate(root_panel.size*0.75)
        #level = game_map.generate(root_panel.size*1.025)
        level = game_map.generate(ecs, LEVEL_SIZE)
        ecs.add_level(level)

        loop(wrapper, root_panel, ecs)

