import functools
import logging
import uuid

from .geometry import Size

from .tilesheets import TERMINAL_12x12_CP
from .wrappers import TcodWrapper

from .rng import rng, generate_seed
from .procgen.dungeons import RandomDungeonLevelGenerator, RogueGridLevelGenerator, BSPLevelGenerator
from .procgen.dungeons import StaticLevel

from . import components
from .data_loaders import DataLoader
from .ecs import ECS
from .entities_spawner import EntitiesSpawner
from .events.keys import KeyBindings
from .tiles.tilesets import Tileset
from .spatial_index import SpatialIndex
from . import systems

from .render import ConsoleRenderingSystem


log = logging.getLogger(__name__)


ENTITIES_DATA_FN = 'entities.yaml'
TILESET_DATA_FN = 'tiles.yaml'
KEY_BINDINGS_DATA_FN = 'keys.yaml'


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
# SEED = uuid.UUID("63a630e9-6548-4291-a62a-fb29e1331a09") # Can't connect!
# SEED = uuid.UUID("9996ca9c-a64b-4963-a42b-4566036aa067") # Lower part bitmasking...
# SEED = uuid.UUID("40e5d1ea-0c1b-43c6-acd5-b561798a3a49")


def run():
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

    # Pregenerate some levels for stress testing
    # level, starting_position = level_generator.generate()
    # for depth in range(1, 50):
    #     level, starting_position = level_generator.generate(depth=depth)

    # Register systems
    # NOTE: Systems are run in order they were registered
    for system in [
        systems.LevelsSystem(ecs, level_generator),

        systems.ActionsQueueSystem(ecs),
        systems.TakeActionsSystem(ecs),

        systems.QuitSystem(ecs),
        systems.MeleeCombatSystem(ecs),
        systems.RestingSystem(ecs),
        systems.MovementSystem(ecs),
        systems.OperateSystem(ecs),

        systems.IndexingSystem(ecs),
        systems.VisibilitySystem(ecs),

        systems.ActionsPerformedSystem(ecs),

        systems.AnimationsSystem(ecs),
        systems.TTLSystem(ecs),

        systems.RunStateSystem(ecs),
    ]:
        ecs.register(system)

    # Create player
    player = ecs.resources.spawner.create('actors.PLAYER')

    wrapper = TcodWrapper(
        console_size=CONSOLE_SIZE,
        palette=ecs.resources.tileset.palette,
        tilesheet=TERMINAL_12x12_CP,
        resizable=False,
        title='Rogal test'
    )

    with wrapper as wrapper:
        ecs.resources.wrapper = wrapper

        # Register rendering system
        rendering_system = ConsoleRenderingSystem(ecs)
        ecs.register(rendering_system)

        events_handlers_system = systems.EventsHandlersSystem(ecs)
        ecs.register(events_handlers_system)

        ecs.run()

