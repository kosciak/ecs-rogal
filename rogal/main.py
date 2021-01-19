import functools
import logging
import time
import os.path
import uuid

import tcod

from .geometry import Position, Size
from .tilesheets import TERMINAL_12x12_CP

from .wrappers import TcodWrapper
from . import keys

from .procgen.dungeons import RandomDungeonLevelGenerator, RogueGridLevelGenerator, BSPLevelGenerator
from .procgen.dungeons import StaticLevel

from .ecs import ECS
from . import components
from .entities import Entities
from .renderable import Tileset
from . import systems

from .game_loop import GameLoop

from .render import Camera, render_message_log

from .player import try_move

from .utils import perf


log = logging.getLogger(__name__)


DATA_DIR = 'data'

ENTITIES_DATA_FN = os.path.join(DATA_DIR, 'entities.yaml')
TILESET_DATA_FN = os.path.join(DATA_DIR, 'tiles.yaml')


CONSOLE_SIZE = Size(80, 48)
#CONSOLE_SIZE = Size(80, 60)

CAMERA_SIZE = Size(15, 15)

LEVEL_SIZE = Size(21,21)
LEVEL_SIZE = Size(CONSOLE_SIZE.width-2, CONSOLE_SIZE.height-14)

LEVEL_GENERATOR_CLS = RandomDungeonLevelGenerator
# LEVEL_GENERATOR_CLS = RogueGridLevelGenerator
# LEVEL_GENERATOR_CLS = BSPLevelGenerator
# LEVEL_GENERATOR_CLS = StaticLevel

SEED = None
# SEED = uuid.UUID("f6df641c-d526-4037-8ee8-c9866ba1199d")


@perf.timeit
def render(wrapper, root_panel, tileset, ecs, player):
    if not player:
        return False
    locations = ecs.manage(components.Location)
    location = locations.get(player)
    level = ecs.levels.get(location.level_id)

    log.debug(f'Render @ {time.time()}')
    root_panel.clear()
    camera, message_log = root_panel.split(bottom=12)
    #camera = root_panel.create_panel(Position(10,10), CAMERA_SIZE)

    render_message_log(message_log.framed('logs'))

    cam = Camera(camera.framed('mapcam'), tileset, ecs)
    cam.render(player, level)

    # Show rendered panel
    wrapper.flush(root_panel)
    return True


def handle_events(wrapper, ecs, player, wait=None):
    for event in wrapper.events(wait):
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
                return try_move(ecs, player, direction)

        if event.type == 'QUIT':
            log.warning('Quitting...')
            raise SystemExit()


def loop(wrapper, root_panel, tileset, ecs):
    renderer = functools.partial(render, wrapper, root_panel, tileset, ecs)
    input_handler = functools.partial(handle_events, wrapper, ecs)
    game_loop = GameLoop(ecs, renderer, input_handler)
    game_loop.join()


def run():
    # ECS initialization
    ecs = ECS()

    # Tileset initialization

    tileset = Tileset()

    # Entities initialization

    entities = Entities(ecs, tileset)

    # Register systems
    # NOTE: Systems are run in order they were registered
    ecs.register(systems.ParticlesSystem(ecs, entities))

    ecs.register(systems.ActionsQueueSystem(ecs, entities))

    ecs.register(systems.MeleeCombatSystem(ecs, entities))
    ecs.register(systems.MovementSystem(ecs, entities))
    ecs.register(systems.OperateSystem(ecs, entities))

    ecs.register(systems.MapIndexingSystem(ecs, entities))
    ecs.register(systems.VisibilitySystem(ecs, entities))

    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=tileset.palette,
        tilesheet=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    with wrapper as wrapper:
        root_panel = wrapper.create_panel()

        # Level(s) generation
        level = LEVEL_GENERATOR_CLS(entities, LEVEL_SIZE, seed=SEED).generate()
        ecs.add_level(level)

        loop(wrapper, root_panel, tileset, ecs)

