import functools
import logging
import os.path
import uuid

from .geometry import Position, Size
from .tilesheets import TERMINAL_12x12_CP

from .wrappers import TcodWrapper

from .rng import generate_seed
from .procgen.dungeons import RandomDungeonLevelGenerator, RogueGridLevelGenerator, BSPLevelGenerator
from .procgen.dungeons import StaticLevel

from . import components
from .ecs import ECS
from .entities import Entities
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
# SEED = uuid.UUID("f6df641c-d526-4037-8ee8-c9866ba1199d")


def register_systems(ecs, entities):
    # NOTE: Systems are run in order they were registered
    for system in [
        systems.ParticlesSystem,

        systems.ActionsQueueSystem,

        systems.MeleeCombatSystem,
        systems.MovementSystem,
        systems.OperateSystem,

        systems.MapIndexingSystem,
        systems.VisibilitySystem,
    ]:
        ecs.register(system(ecs, entities))


def run():
    # Generate seed
    seed = SEED or generate_seed()

    # ECS initialization
    ecs = ECS()

    # Tileset initialization
    tileset = Tileset()

    # Entities initialization
    entities = Entities(ecs, tileset)

    # Register systems
    register_systems(ecs, entities)

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
        level = LEVEL_GENERATOR_CLS(seed, entities, LEVEL_SIZE).generate()
        ecs.add_level(level)

        renderer = Renderer(ecs, wrapper, root_panel, tileset)
        input_handler = PlayerActionsHandler(ecs, wrapper)
        game_loop = GameLoop(ecs, renderer, input_handler)
        game_loop.join()

