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
# SEED = uuid.UUID("f6583dbd-83ce-4654-b0b0-278f13c5493b")
# SEED = uuid.UUID("2d88638b-0391-4a4e-b345-ae2bb6da0070")
# SEED = uuid.UUID("acce1b71-a9a8-4558-9538-3f0b4a1a2976")
# SEED = uuid.UUID("7cde54b5-6602-41f3-a8a3-a9e0ffc1817e")
# SEED = uuid.UUID("7c0401fe-ffcd-4744-a5b3-ea5114a32b56")
# SEED = uuid.UUID("63a630e9-6548-4291-a62a-fb29e1331a09") # Can't connect!
# SEED = uuid.UUID("9996ca9c-a64b-4963-a42b-4566036aa067") # Lower part bitmasking...


def register_systems(ecs, spatial, spawner):
    # NOTE: Systems are run in order they were registered
    for system in [
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
    # Generate seed
    seed = SEED or generate_seed()
    rng.seed(seed, dump='rng')

    # ECS initialization
    ecs = ECS()

    # Spatial index
    spatial = SpatialIndex(ecs)

    # Tileset initialization
    tileset = Tileset()

    # Entities spawner initialization
    spawner = EntitiesSpawner(ecs, spatial, tileset)

    player = spawner.create('actors.PLAYER')

    # Level generator
    level_generator = LEVEL_GENERATOR_CLS(seed, spawner, LEVEL_SIZE)

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
        level = level_generator.generate(player=player)
        # for depth in range(1, 55):
        #     level = level_generator.generate(depth=depth)

        renderer = Renderer(ecs, spatial, wrapper, root_panel, tileset)
        input_handler = PlayerActionsHandler(ecs, spatial, wrapper)
        game_loop = GameLoop(ecs, spatial, renderer, input_handler)
        game_loop.join()

