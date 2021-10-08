import logging

from ..geometry import Size
from ..utils import perf

from .core import Generator
from .rooms import RandomlyPlacedRoomsGenerator, GridRoomsGenerator, BSPRoomsGenerator
from .rooms_connectors import RandomToNearestRoomsConnector, FollowToNearestRoomsConnector, BSPRoomsConnector


log = logging.getLogger(__name__)


class TerrainGenerator(Generator):

    def __init__(self, rng, ecs, default_fill, room_wall, room_floor, corridor_floor):
        super().__init__(rng)
        self.spawner = ecs.resources.spawner
        self.spatial = ecs.resources.spatial

        self.default_fill = default_fill
        self.room_wall = room_wall
        self.room_floor = room_floor
        self.corridor_floor = corridor_floor

    def fill_default(self, terrain):
        """Fill whole area with given terrain."""
        terrain[:] = self.spawner.get(self.default_fill)

    def dig_rooms(self, terrain, rooms):
        """Dig rooms."""
        wall = self.spawner.get(self.room_wall)
        floor = self.spawner.get(self.room_floor)
        for room in rooms:
            room.set_walls(terrain, wall)
            room.dig_floor(terrain, floor)

    def dig_corridors(self, terrain, corridors):
        """Dig corridors."""
        floor = self.spawner.get(self.corridor_floor)
        for corridor in corridors:
            # NOTE: No set_walls for now since corridors would be blocked by walls when crossing!
            corridor.dig_floor(terrain, floor)

    def generate(self, size, rooms, corridors):
        terrain = self.spatial.init_terrain(size)
        self.fill_default(terrain)
        self.dig_rooms(terrain, rooms)
        self.dig_corridors(terrain, corridors)
        return terrain


class EntitiesSpawningGenerator(Generator):

    def __init__(self, rng, ecs):
        super().__init__(rng)
        self.spawner = ecs.resources.spawner
        self.spatial = ecs.resources.spatial

    def spawn_closed_door(self, level_id, position, populated=False):
        level = self.spatial.get_level(level_id)
        level.terrain[position] = self.spawner.get('terrain.DOOR')
        if not populated:
            return self.spawner.create_and_spawn('props.CLOSED_DOOR', level_id, position)

    def spawn_monster(self, level_id, position):
        monster = self.rng.choice([
            'actors.MONSTER',
            'actors.BAT',
            'actors.SNAIL',
        ])
        return self.spawner.create_and_spawn(monster, level_id, position)

    def generate_doors(self, level_id, corridors, populated=False):
        for corridor in corridors:
            if corridor.length == 1:
                # Always spawn door in corridors with length == 1
                position = corridor.get_position(0)
                if position in corridor.allowed_doors:
                    self.spawn_closed_door(level_id, position, populated)
            elif corridor.length > 1:
                # Never spawn doors in corridors with length == 2
                # Otherwise there's 25% chance of door on each end of corridor
                if self.rng.random() < .5:
                    position = corridor.get_position(0)
                    if position in corridor.allowed_doors:
                        self.spawn_closed_door(level_id, position, populated)
                if self.rng.random() < .5:
                    position = corridor.get_position(-1)
                    if position in corridor.allowed_doors:
                        self.spawn_closed_door(level_id, position, populated)

    def generate_monsters(self, level_id, rooms, occupied):
        for room in rooms:
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
                self.spawn_monster(level_id, position)
        return occupied

    def generate(self, level_id, rooms, corridors, populated=False):
        """Spawn entities."""
        self.generate_doors(level_id, corridors, populated)

        # Spawn Player in the center of the first room
        starting_position = rooms[0].center

        # Occupied postions
        occupied = {starting_position, }
        if not populated:
            occupied = self.generate_monsters(level_id, rooms, occupied)

        return starting_position


class DoorsEverywhereEntitiesSpawningGenerator(EntitiesSpawningGenerator):

    def generate_doors(self, level, corridors, populated=False):
        for corridor in corridors:
            for position in corridor.allowed_doors:
                self.spawn_closed_door(level, position)


class RoomsLevelGenerator(Generator):

    DEFAULT_FILL = 'terrain.STONE_WALL'
    ROOM_WALL = 'terrain.STONE_WALL'
    ROOM_FLOOR = 'terrain.STONE_FLOOR'
    CORRIDOR_FLOOR = 'terrain.STONE_FLOOR'

    def __init__(self, seed, ecs, size):
        super().__init__(seed=seed)

        self.spawner = ecs.resources.spawner
        self.spatial = ecs.resources.spatial

        self.size = size # TODO: Should I stay or should I go?

        self.rooms_generator = None
        self.rooms_connector = None

        self.terrain_genenrator = TerrainGenerator(
            self.rng, ecs,
            self.DEFAULT_FILL,
            self.ROOM_WALL, self.ROOM_FLOOR,
            self.CORRIDOR_FLOOR,
        )
        self.entities_generator = EntitiesSpawningGenerator(self.rng, ecs)

    def init_level(self, level_id=None, size=None):
        # Generate UUID using rng, so it will be same UUID using same rng
        level_id = level_id or self.rng.uuid4()
        # Reseed generator to just generated level_id, this way levels with same seed are gennerated same way
        self.rng.seed(level_id)
        return level_id

    def generate_rooms(self):
        log.info(f'Generating rooms: {self.rooms_generator}')
        rooms_distances = self.rooms_generator.generate(self.size)
        return rooms_distances

    def connect_rooms(self, rooms_distances):
        log.info(f'Connecting rooms: {self.rooms_connector}')
        corridors = self.rooms_connector.connect_rooms(rooms_distances)
        return corridors

    def generate_terrain(self, rooms, corridors):
        return self.terrain_genenrator.generate(self.size, rooms, corridors)

    def generate_entities(self, level_id, rooms, corridors, populated=False):
        return self.entities_generator.generate(level_id, rooms, corridors, populated)

    def generate(self, level_id=None, depth=0, populated=False):
        level_id = self.init_level(level_id=level_id)
        log.info(f'Generating level: {level_id}')

        rooms_distances = self.generate_rooms()
        rooms = list(rooms_distances.keys())
        corridors = self.connect_rooms(rooms_distances)
        terrain = self.generate_terrain(rooms, corridors)

        level_id = self.spatial.create_level(level_id, depth, terrain)

        starting_position = self.generate_entities(level_id, rooms, corridors, populated)

        return level_id, starting_position



class RandomDungeonLevelGenerator(RoomsLevelGenerator):

    """LevelGenerator creating random rooms connected with straight corridors."""

    def __init__(self, seed, ecs, size):
        super().__init__(seed, ecs, size)

        self.rooms_generator = RandomlyPlacedRoomsGenerator(self.rng)
        self.rooms_connector = RandomToNearestRoomsConnector(self.rng)


class RogueGridLevelGenerator(RoomsLevelGenerator):

    DEFAULT_FILL = 'terrain.VOID'
    ROOM_WALL = 'terrain.STONE_WALL'
    ROOM_FLOOR = 'terrain.STONE_FLOOR'
    CORRIDOR_FLOOR = 'terrain.ROCK_FLOOR'

    def __init__(self, seed, ecs, size):
        super().__init__(seed, ecs, size)

        self.rooms_generator = GridRoomsGenerator(self.rng)
        self.rooms_connector = FollowToNearestRoomsConnector(self.rng)
        self.entities_generator = DoorsEverywhereEntitiesSpawningGenerator(self.rng, ecs)


class BSPLevelGenerator(RoomsLevelGenerator):

    def __init__(self, seed, ecs, size):
        super().__init__(seed, ecs, size)

        self.rooms_generator = BSPRoomsGenerator(self.rng)
        self.rooms_connector = BSPRoomsConnector(self.rng)


class StaticLevel(RoomsLevelGenerator):

    def generate_rooms(self):
        from ..geometry import Position
        from .rooms import Room
        center = self.level.center
        rooms = [
            Room(
                Position(center.x-10, center.y-10),
                Size(21, 10),
            ),
            Room(
                Position(center.x-10, center.y+1),
                Size(21, 10)
            ),
        ]
        rooms_distances = {room: 1 for room in rooms}
        return rooms_distances

    def connect_rooms(self, rooms_distances):
        from ..geometry import Position
        from .corridors import VerticalCorridor
        center = self.level.center
        corridors = [
            VerticalCorridor(center, 1),
            VerticalCorridor(Position(center.x-6, center.y), 1),
            VerticalCorridor(Position(center.x+6, center.y), 1),
        ]
        for corridor in corridors:
            corridor.allow_door(0)
        return corridors

