import functools
import logging
import os.path
import uuid

from .geometry import Position, Size
from .tilesheets import TERMINAL_12x12_CP

from .wrappers import TcodWrapper

from .rng import rng, generate_seed
from .procgen.dungeons import RandomDungeonLevelGenerator, RogueGridLevelGenerator, BSPLevelGenerator
from .procgen.dungeons import StaticLevel

from . import components
from .ecs import ECS
from .spatial_index import SpatialIndex
from .entities_spawner import EntitiesSpawner
from .renderable import Tileset
from . import systems

from .game_loop import GameLoop

from .render import Renderer

from .input_handlers import PlayerActionsHandler


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
# SEED = uuid.UUID("63a630e9-6548-4291-a62a-fb29e1331a09") # Can't connect!
# SEED = uuid.UUID("9996ca9c-a64b-4963-a42b-4566036aa067") # Lower part bitmasking...
# SEED = uuid.UUID("40e5d1ea-0c1b-43c6-acd5-b561798a3a49")


def register_systems(ecs, spatial, spawner):
    # Generate seed
    seed = SEED or generate_seed()
    rng.seed(seed, dump='rng')

    # Level generator
    level_generator = LEVEL_GENERATOR_CLS(seed, spawner, LEVEL_SIZE)

    # NOTE: Systems are run in order they were registered
    for system in [
        systems.LevelsSystem(ecs, spatial, level_generator),

        systems.ParticlesSystem(ecs, spatial),

        systems.ActionsQueueSystem(ecs),

        systems.MeleeCombatSystem(ecs, spawner),
        systems.MovementSystem(ecs, spatial),
        systems.OperateSystem(ecs),

        systems.IndexingSystem(ecs, spatial),
        systems.VisibilitySystem(ecs, spatial),

        systems.QueuecCleanupSystem(ecs),
    ]:
        ecs.register(system)


def run():

    # ECS initialization
    ecs = ECS()

    # Spatial index
    spatial = SpatialIndex(ecs)

    # Tileset initialization
    tileset = Tileset()

    # Entities spawner initialization
    spawner = EntitiesSpawner(ecs, spatial, tileset)

    player = spawner.create('actors.PLAYER')

    # Register systems
    register_systems(ecs, spatial, spawner)

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
        # level, starting_position = level_generator.generate(player=player)
        # for depth in range(1, 55):
        #     level, starting_position = level_generator.generate(depth=depth)

        renderer = Renderer(ecs, spatial, wrapper, root_panel, tileset)
        input_handler = PlayerActionsHandler(ecs, spatial, wrapper)
        game_loop = GameLoop(ecs, spatial, renderer, input_handler)
        game_loop.join()

