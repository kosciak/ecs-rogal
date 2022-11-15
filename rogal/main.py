import logging
import uuid

from .geometry import Size

from .wrappers.tcod import TcodWrapper
from .wrappers.curses import CursesWrapper
from .wrappers.term import TermWrapper

from .data import data_store

from .rng import rng, generate_seed

from .procgen.dungeons import RandomDungeonLevelGenerator, RogueGridLevelGenerator, BSPLevelGenerator
from .procgen.dungeons import StaticLevel

from .ecs import ECS

from .toolkit.builder import WidgetsBuilder

from .events.managers import EventsManager

from .colors.managers import ColorsManager

from .entities_spawner import EntitiesSpawner

from .data.loaders import DataLoader
from .tiles.tilesets import Tileset

from .spatial.spatial_index import SpatialIndex

from . import events
from . import signals
from . import ui

from . import systems


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


ENTITIES_DATA_FN = 'entities.yaml'
TILESET_DATA_FN = 'tiles.yaml'

data_store.register_source(data='data.yaml')

CONSOLE_SIZE = Size(80, 48)
#CONSOLE_SIZE = Size(80, 60)

LEVEL_SIZE = Size(21,21)
LEVEL_SIZE = Size(CONSOLE_SIZE.width-2, CONSOLE_SIZE.height-14)

LEVEL_GENERATOR_CLS = RandomDungeonLevelGenerator
# LEVEL_GENERATOR_CLS = RogueGridLevelGenerator
# LEVEL_GENERATOR_CLS = BSPLevelGenerator
# LEVEL_GENERATOR_CLS = StaticLevel

SEED = None
# SEED = uuid.UUID("63a630e9-6548-4291-a62a-fb29e1331a09") # Can't connect!
# SEED = uuid.UUID("9996ca9c-a64b-4963-a42b-4566036aa067") # Lower part bitmasking...
# SEED = uuid.UUID("40e5d1ea-0c1b-43c6-acd5-b561798a3a49")
# SEED = uuid.UUID("6779231d-89c3-43be-93b2-41f9212f2848")
SEED = uuid.UUID('5829028d-61c1-4e8d-ac96-26236d1fd6a1')


WRAPPERS = {
    'tcod': TcodWrapper,
    'curses': CursesWrapper,
    'term': TermWrapper,
}


def print_charset(charset):
    row = []
    for char in charset:
        if char == 0x7f:
            char = 32
        row.append(chr(char or 32))
        if len(row) >= 16*2:
            msg_log.info(''.join(row))
            row = []


def initialize_wrapper(ecs, wrapper):
    # Tileset initialization
    ecs.resources.register(
        tileset=Tileset(DataLoader(TILESET_DATA_FN)),
    )
    ecs.resources.register(
        colors_manager=ColorsManager(ecs.resources.tileset.palette),
    )

    # Initialize Wrapper
    wrapper_cls = WRAPPERS[wrapper]
    ecs.resources.register(
        wrapper=wrapper_cls(
            console_size=CONSOLE_SIZE,
            colors_manager=ecs.resources.colors_manager,
            tiles_sources=ecs.resources.tileset.tiles_sources,
            resizable=False,
            title='Rogal test'
        ),
    )


def initialize_ui(ecs, inital_screen):
    # Console UI manager
    ui.initialize(ecs)

    # Input events
    events.initialize(ecs)
    ecs.resources.events_manager.add_source(ecs.resources.wrapper)

    # Signals handling
    signals.initialize(ecs)

    # Widgets builder
    ecs.resources.register(
        widgets_builder = WidgetsBuilder(ecs),
    )

    ecs.register(
        systems.run_state.RenderStateSystem(ecs),
    )

    ecs.resources.ui_manager.create(inital_screen)


def initialize_game(ecs, seed):
    # Spatial index
    ecs.resources.spatial = SpatialIndex(ecs)

    # Entities spawner initialization
    ecs.resources.spawner = EntitiesSpawner(ecs, DataLoader(ENTITIES_DATA_FN))

    # Level generator
    ecs.resources.level_generator = LEVEL_GENERATOR_CLS(seed, ecs, LEVEL_SIZE)

    # Create player
    player = ecs.resources.spawner.create('actors.PLAYER')

    # Pregenerate some levels for stress testing
    # level, starting_position = level_generator.generate()
    # for depth in range(1, 50):
    #     level, starting_position = level_generator.generate(depth=depth)

    # Register systems
    # NOTE: Systems are run in order they were registered
    ecs.register(
        # Core engine related systems
        # NOTE: Input events and rendering MUST be done in main thread
        systems.real_time.TTLSystem(ecs),

        systems.run_state.ActionsLoopStateSystem(ecs),
        systems.run_state.AnimationsStateSystem(ecs),

        systems.commands.QuitSystem(ecs),

        # Game related systems
        systems.levels.LevelsSystem(ecs),

        systems.actions.ActionsQueueSystem(ecs),
        systems.actions.TakeActionsSystem(ecs),

        systems.actions.MeleeCombatSystem(ecs),
        systems.actions.RestingSystem(ecs),
        systems.actions.MovementSystem(ecs),
        systems.actions.OperateSystem(ecs),

        systems.spatial.SpatialIndexingSystem(ecs),

        systems.awerness.InvalidateViewshedsSystem(ecs),
        systems.awerness.VisibilitySystem(ecs),
        systems.awerness.RevealLevelSystem(ecs),

        systems.actions.ActionsPerformedSystem(ecs),
    )


def run(wrapper):
    # Generate seed and init RNG
    seed = SEED or generate_seed()
    rng.seed(seed, dump='rng')

    # ECS initialization
    ecs = ECS()

    initialize_wrapper(ecs, wrapper)
    initialize_ui(ecs, 'IN_GAME')
    initialize_game(ecs, seed)

    # from .data import UnicodeBlocks
    from .data import Charsets
    print_charset(Charsets.CP437)

    with ecs.resources.wrapper:
        ecs.run()

