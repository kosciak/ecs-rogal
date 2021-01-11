import logging
import uuid

from .. import entities
from ..game_map import GameMap
from ..geometry import Size
from ..terrain import Terrain

from .core import Generator
from .rooms import GridRoomsGenerator, RandomlyPlacedRoomsGenerator, BSPRoomsGenerator
from .rooms_connectors import RandomToNearestRoomsConnector, FollowToNearestRoomsConnector


log = logging.getLogger(__name__)


SEED = None
# SEED = uuid.UUID("fb3d4f1c-b8ce-4769-b666-1e776532ab62")


class RoomsLevelGenerator(Generator):

    def __init__(self, ecs, size, depth=0, seed=None):
        super().__init__(seed=seed)

        self.ecs = ecs

        self.size = size
        self.depth = depth
        self.level = GameMap.create(self.size, self.depth)

        self.distances = {}
        self.rooms = []
        self.rooms_generator = None

        self.corridors = []
        self.rooms_connector = None

    def generate_rooms(self):
        self.distances = self.rooms_generator.generate()
        self.rooms = list(self.distances.keys())

    def connect_rooms(self):
        self.corridors = self.rooms_connector.connect_rooms(self.distances)

    def fill(self, terrain):
        """Fill whole level with given terrain."""
        self.level.terrain[:] = terrain.id

    def dig_rooms(self, wall, floor):
        """Dig rooms."""
        for room in self.rooms:
            room.set_walls(self.level, wall)
            room.dig_floor(self.level, floor)

    def dig_corridors(self, floor):
        """Dig corridors."""
        for corridor in self.corridors:
            # NOTE: No set_walls for now since corridors would be blocked by walls when crossing!
            corridor.dig_floor(self.level, floor)

    def spawn_closed_door(self, position):
        closed_door = entities.create(self.ecs, entities.CLOSED_DOOR)
        entities.spawn(self.ecs, closed_door, self.level.id, position)

    def spawn_player(self, position):
        player = entities.create_player(self.ecs)
        entities.spawn(self.ecs, player, self.level.id, self.rooms[0].center)

    def spawn_monster(self, position):
        monster = entities.create_monster(self.ecs)
        entities.spawn(self.ecs, monster, self.level.id, position)

    def spawn_entities(self):
        raise NotImplementedError()

    def generate(self):
        self.generate_rooms()
        self.connect_rooms()

        self.fill(Terrain.VOID)
        self.dig_rooms(wall=Terrain.STONE_WALL, floor=Terrain.STONE_FLOOR)
        self.dig_corridors(floor=Terrain.STONE_FLOOR)

        self.spawn_entities()

        self.level.revealed[:] = 1
        return self.level


class RoomsWithStraightCorridorsLevelGenerator(RoomsLevelGenerator):

    """LevelGenerator creating random rooms connected with straight corridors."""

    def __init__(self, ecs, size, depth=0, seed=SEED):
        super().__init__(ecs, size, depth, seed=seed)

        # self.rooms_generator = RandomlyPlacedRoomsGenerator(self.rng, self.level)
        # self.rooms_generator = GridRoomsGenerator(self.rng, self.level, Size(3, 3))
        # self.rooms_generator = GridRoomsGenerator(self.rng, self.level, Size(4, 3))
        # self.rooms_generator = GridRoomsGenerator(self.rng, self.level, Size(5, 5))
        self.rooms_generator = BSPRoomsGenerator(self.rng, self.level)

        # self.rooms_connector = RandomToNearestRoomsConnector(self.rng, self.level.size)
        self.rooms_connector = FollowToNearestRoomsConnector(self.rng, self.level.size)

    def spawn_entities(self):
        """Spawn entities."""
        # Occupied postions
        occupied = set()

        # Spawn Player in the center of the first room
        position = self.rooms[0].center
        self.spawn_player(position)
        occupied.add(position)

        # Doors
        for corridor in self.corridors:
            if corridor.length == 1:
                # Always spawn door in corridors with length == 1
                position = corridor.get_position(0)
                if position in corridor.allowed_doors:
                    self.spawn_closed_door(position)
            elif corridor.length > 1:
                # Never spawn doors in corridors with length == 2
                # Otherwise there's 25% chance of door on each end of corridor
                if self.rng.random() < .5:
                    position = corridor.get_position(0)
                    if position in corridor.allowed_doors:
                        self.spawn_closed_door(position)
                if self.rng.random() < .5:
                    position = corridor.get_position(-1)
                    if position in corridor.allowed_doors:
                        self.spawn_closed_door(position)

        # Monsters
        for room in self.rooms:
            area = room.inner.area
            min_monster_area = 5**2
            min_monsters_num = 0
            max_monsters_num = area//min_monster_area
            if max_monsters_num > 3:
                min_monsters_num = 1
            max_monsters_num = min(3, max_monsters_num)
            monsters_num = self.rng.randint(min_monsters_num, max_monsters_num)
            room_positions = list(room.inner.positions)
            for i in range(monsters_num):
                position = self.rng.choice(room_positions)
                while position in occupied:
                    position = self.rng.choice(room_positions)
                occupied.add(position)
                self.spawn_monster(position)


LevelGenerator = RoomsWithStraightCorridorsLevelGenerator


def generate_static_level(ecs, size):
    from ..geometry import Position

    level = GameMap.create(size, 0)

    # Terrain layout
    level.terrain[:] = Terrain.STONE_WALL.id
    level.terrain[1:-1, 1:-1] = Terrain.STONE_FLOOR.id
    level.terrain[-3:-1, 1:-1] = Terrain.SHALLOW_WATER.id
    level.terrain[1: -1, level.height//2] = Terrain.STONE_WALL.id
    level.terrain[level.center] = Terrain.STONE_FLOOR.id
    level.terrain[level.width//4, level.height//2] = Terrain.STONE_FLOOR.id
    level.terrain[level.width//4*3, level.height//2] = Terrain.STONE_FLOOR.id

    # Entities Spawning
    closed_door = entities.create(ecs, entities.CLOSED_DOOR)
    entities.spawn(ecs, closed_door, level.id, level.center)

    player = entities.create(ecs, entities.PLAYER)
    entities.spawn(ecs, player, level.id, Position(3,3))

    for offset in [(-2,-2), (2,2), (-3,3), (3,-3)]:
        monster = entities.create(ecs, entities.MONSTER)
        position = level.center + Position(*offset)
        entities.spawn(ecs, monster, level.id, position)

    return level

