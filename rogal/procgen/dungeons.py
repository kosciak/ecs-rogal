import logging
import uuid

from ..level import Level
from ..geometry import Size
from ..utils import perf

from .core import Generator
from .rooms import RandomlyPlacedRoomsGenerator, GridRoomsGenerator, BSPRoomsGenerator
from .rooms_connectors import RandomToNearestRoomsConnector, FollowToNearestRoomsConnector, BSPRoomsConnector


log = logging.getLogger(__name__)


class RoomsLevelGenerator(Generator):

    def __init__(self, seed, spawner, size):
        super().__init__(seed=seed)

        self.spawner = spawner

        self.size = size
        self._level = None

        self.rooms = []
        self.rooms_generator = None

        self.corridors = []
        self.rooms_connector = None

    def clear(self):
        self.rooms = []
        self.corridors = []

    def init_level(self, level_id=None, size=None, depth=0):
        # Generate UUID using rng, so it will be same UUID using same rng
        level_id = self.rng.uuid4()
        size = size or self.size
        level = Level(level_id, size, depth)
        # Reseed generator to just generated level_id, this way levels with same seed are gennerated same way
        self.rng.seed(level_id)
        return level

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        self.clear()

    def generate_rooms(self):
        log.info(f'Generating rooms: {self.rooms_generator}')
        rooms_distances = self.rooms_generator.generate(self.level)
        self.rooms = list(rooms_distances.keys())
        return rooms_distances

    def connect_rooms(self, rooms_distances):
        log.info(f'Connecting rooms: {self.rooms_connector}')
        self.corridors = self.rooms_connector.connect_rooms(rooms_distances)

    def fill(self, terrain):
        """Fill whole level with given terrain."""
        self.level.terrain[:] = self.spawner.get(terrain)

    def dig_rooms(self, wall, floor):
        """Dig rooms."""
        wall = self.spawner.get(wall)
        floor = self.spawner.get(floor)
        for room in self.rooms:
            room.set_walls(self.level, wall)
            room.dig_floor(self.level, floor)

    def dig_corridors(self, floor):
        """Dig corridors."""
        floor = self.spawner.get(floor)
        for corridor in self.corridors:
            # NOTE: No set_walls for now since corridors would be blocked by walls when crossing!
            corridor.dig_floor(self.level, floor)

    def spawn_entities(self, player=None):
        raise NotImplementedError()

    def generate(self, depth=0, player=None):
        self.level = self.init_level(size=self.size, depth=depth)
        log.info(f'Generating: {self.level}')

        rooms_distances = self.generate_rooms()
        self.connect_rooms(rooms_distances)

        self.fill('terrain.STONE_WALL')
        # self.fill('terrain.VOID')

        self.dig_rooms(wall='terrain.STONE_WALL', floor='terrain.STONE_FLOOR')
        self.dig_corridors(floor='terrain.STONE_FLOOR')
        # self.dig_corridors(floor='terrain.ROCK_FLOOR')

        self.spawn_entities(player)

        # self.level.reveal()
        return self.level


class RandomEntitiesMixin:

    # TODO: Move to separate EntitiesSpawner class?

    def spawn_closed_door(self, position):
        self.level.terrain[position] = self.spawner.get('terrain.DOOR')
        return self.spawner.create_and_spawn('props.CLOSED_DOOR', self.level.id, position)

    def spawn_player(self, position=None, player=None):
        if player is None:
            return
        position = position or self.rooms[0].center
        return self.spawner.spawn(player, self.level.id, position)

    def spawn_monster(self, position):
        monster = self.rng.choice([
            'actors.MONSTER',
            'actors.BAT',
            'actors.SNAIL',
        ])
        return self.spawner.create_and_spawn(monster, self.level.id, position)

    def spawn_entities(self, player=None):
        """Spawn entities."""
        # Occupied postions
        occupied = set()

        # Spawn Player in the center of the first room
        position = self.rooms[0].center
        self.spawn_player(position, player)
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


class RandomDungeonLevelGenerator(RandomEntitiesMixin, RoomsLevelGenerator):

    """LevelGenerator creating random rooms connected with straight corridors."""

    def __init__(self, seed, spawner, size):
        super().__init__(seed, spawner, size)

        self.rooms_generator = RandomlyPlacedRoomsGenerator(self.rng)
        self.rooms_connector = RandomToNearestRoomsConnector(self.rng)


class RogueGridLevelGenerator(RandomEntitiesMixin, RoomsLevelGenerator):

    def __init__(self, seed, spawner, size):
        super().__init__(seed, spawner, size)

        self.rooms_generator = GridRoomsGenerator(self.rng)
        self.rooms_connector = FollowToNearestRoomsConnector(self.rng)


class BSPLevelGenerator(RandomEntitiesMixin, RoomsLevelGenerator):

    def __init__(self, seed, spawner, size):
        super().__init__(seed, spawner, size)

        self.rooms_generator = BSPRoomsGenerator(self.rng)
        self.rooms_connector = BSPRoomsConnector(self.rng)


class StaticLevel(RandomEntitiesMixin, RoomsLevelGenerator):

    def generate_rooms(self):
        from ..geometry import Position
        from .rooms import Room
        center = self.level.center
        self.rooms = [
            Room(
                Position(center.x-10, center.y-10),
                Size(21, 10),
            ),
            Room(
                Position(center.x-10, center.y+1),
                Size(21, 10)
            ),
        ]

    def connect_rooms(self, rooms_distances):
        from ..geometry import Position
        from .corridors import VerticalCorridor
        center = self.level.center
        self.corridors = [
            VerticalCorridor(center, 1),
            VerticalCorridor(Position(center.x-6, center.y), 1),
            VerticalCorridor(Position(center.x+6, center.y), 1),
        ]
        for corridor in self.corridors:
            corridor.allow_door(0)

