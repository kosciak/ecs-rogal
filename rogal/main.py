import logging
import uuid

from .geometry import Size

from .wrappers.tcod import TcodWrapper
from .wrappers.curses import CursesWrapper
from .wrappers.term import TermWrapper

from .data import register_data

from .rng import rng, generate_seed
from .procgen.dungeons import RandomDungeonLevelGenerator, RogueGridLevelGenerator, BSPLevelGenerator
from .procgen.dungeons import StaticLevel

from . import components
from .console import ui
from .data.loaders import DataLoader
from .ecs import ECS
from .entities_spawner import EntitiesSpawner
from .events.keys import KeyBindings
from .tiles.tilesets import Tileset
from .spatial_index import SpatialIndex
from . import systems

from . import render


log = logging.getLogger(__name__)
msg_log = logging.getLogger('rogal.messages')


ENTITIES_DATA_FN = 'entities.yaml'
TILESET_DATA_FN = 'tiles.yaml'
KEY_BINDINGS_DATA_FN = 'keys.yaml'

register_data(data='data.yaml')

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


def run(wrapper):
    # Generate seed and init RNG
    seed = SEED or generate_seed()
    rng.seed(seed, dump='rng')

    # ECS initialization
    ecs = ECS()

    # Key bindings initialization
    ecs.resources.key_bindings = KeyBindings(DataLoader(KEY_BINDINGS_DATA_FN))

    # Spatial index
    ecs.resources.spatial = SpatialIndex(ecs)

    # Tileset initialization
    ecs.resources.tileset = Tileset(DataLoader(TILESET_DATA_FN))

    # Entities spawner initialization
    ecs.resources.spawner = EntitiesSpawner(ecs, DataLoader(ENTITIES_DATA_FN))

    # Level generator
    level_generator = LEVEL_GENERATOR_CLS(seed, ecs, LEVEL_SIZE)

    # Create player
    player = ecs.resources.spawner.create('actors.PLAYER')

    # Pregenerate some levels for stress testing
    # level, starting_position = level_generator.generate()
    # for depth in range(1, 50):
    #     level, starting_position = level_generator.generate(depth=depth)

    # Initialize Wrapper
    wrapper_cls = WRAPPERS[wrapper]
    ecs.resources.wrapper = wrapper_cls(
        console_size=CONSOLE_SIZE,
        palette=ecs.resources.tileset.palette,
        tiles_sources=ecs.resources.tileset.tiles_sources,
        resizable=False,
        title='Rogal test'
    )

    # Console UI manager
    ecs.resources.ui_manager = ui.UIManager(ecs)

    # Register systems
    # NOTE: Systems are run in order they were registered
    for system in [
        # Core engine related systems
        systems.user_input.InputFocusSystem(ecs),
        systems.user_input.EventsHandlersSystem(ecs),

        systems.real_time.TTLSystem(ecs),

        systems.run_state.UpdateStateSystem(ecs),

        systems.gui.DestroyUIWidgetsSystem(ecs),
        systems.gui.CreateUIWidgetsSystem(ecs),

        systems.console.LayoutSytem(ecs),
        systems.console.RenderingSystem(ecs),

        systems.commands.QuitSystem(ecs),

        # Game related systems
        # TODO: level_generator(s) should be in ecs.resources!
        systems.levels.LevelsSystem(ecs, level_generator),

        systems.actions.ActionsQueueSystem(ecs),
        systems.actions.TakeActionsSystem(ecs),

        systems.actions.MeleeCombatSystem(ecs),
        systems.actions.RestingSystem(ecs),
        systems.actions.MovementSystem(ecs),
        systems.actions.OperateSystem(ecs),

        systems.spatial.IndexingSystem(ecs),

        systems.awerness.InvalidateViewshedsSystem(ecs),
        systems.awerness.VisibilitySystem(ecs),
        systems.awerness.RevealLevelSystem(ecs),

        systems.actions.ActionsPerformedSystem(ecs),

    ]:
        ecs.register(system)

    # from .data import UnicodeBlocks
    from .data import Charsets
    print_charset(Charsets.CP437)

    with ecs.resources.wrapper:
        ecs.run()

