import collections
import logging
import random
import uuid

from . import entities
from .game_map import GameMap
from .geometry import Position, Size, Rectangle
from .terrain import Terrain


log = logging.getLogger(__name__)


MAX_ROOMS = 25

MIN_SIZE = 5
MAX_SIZE = 13

SEED = None
#SEED = uuid.UUID( '137ad920-fd42-470a-a99c-6ed52b7c05b5' )


class OffsetedRectangle(Rectangle):

    INNER_OFFSET = Position.ZERO

    def __init__(self, position, size):
        self.inner = Rectangle(position, size)
        super().__init__(
            Position(position.x-self.INNER_OFFSET.x, position.y-self.INNER_OFFSET.y),
            Size(size.width+self.INNER_OFFSET.x, size.height+self.INNER_OFFSET.y)
        )

    @property
    def center(self):
        return self.inner.center

    def dig_floor(self, level, floor):
        level.terrain[self.inner.x:self.inner.x2, self.inner.y:self.inner.y2] = floor.id


class Room(OffsetedRectangle):

    INNER_OFFSET = Position(1, 1)

    """Rectangular room.

    Left and top border are considered walls, so rooms can share walls with each other when adjecent.

    Room with Size(5, 3) has inner floor area of Size(4, 2) with offset (1, 1)

    #####
    #....
    #....

    """

    def horizontal_share(self, other):
        shared_x = (
            max(self.inner.x, other.inner.x), 
            min(self.inner.x2, other.x2)
        )
        if shared_x[0] > shared_x[1]:
            return []
        return list(range(*shared_x))

    def vertical_share(self, other):
        shared_y = (
            max(self.inner.y, other.inner.y), 
            min(self.inner.y2, other.y2)
        )
        if shared_y[0] > shared_y[1]:
            return []
        return list(range(*shared_y))

    def horizontal_between(self, other):
        min_x = min(self.x2, other.x2)
        max_x = max(self.inner.x, other.inner.x)
        return max_x-min_x

    def vertical_between(self, other):
        min_y = min(self.y2, other.y2)
        max_y = max(self.inner.y, other.inner.y)
        return max_y-min_y

    def set_walls(self, level, wall):
        level.terrain[self.x:self.x2+1, self.y:self.y2+1] = wall.id


class VerticalCorridor(OffsetedRectangle):

    INNER_OFFSET = Position(1, 0)

    """Vertical corridor.

    #.
    #.
    #.

    """

    def __init__(self, position, length):
        self.length = length
        super().__init__(position, Size(1, self.length))

    def get_position(self, length):
        if length < 0:
            length += self.length
        return Position(self.inner.x, self.y+length)


class HorizontalCorridor(OffsetedRectangle):

    INNER_OFFSET = Position(0, 1)

    """Horizontal corridor.

    #####
    .....

    """

    def __init__(self, position, length):
        self.length = length
        super().__init__(position, Size(self.length, 1))

    def get_position(self, length):
        if length < 0:
            length += self.length
        return Position(self.x+length, self.inner.y)


class RoomsWithStraightCorridorsLevelGenerator:

    MIN_ROOM_SIZE = 5
    MAX_ROOM_SIZE_FACTOR = .45
    MAX_ROOM_AREA_FACTOR = .30
    MIN_ROOMS_AREA_FACTOR = .35
    MAX_ROOMS_DISTANCE_FACTOR = .30

    def __init__(self, ecs, size, depth=0, seed=SEED):
        self.ecs = ecs

        self.size = size
        self.depth = depth
        self._level = None

        self.max_room_width = int(self.size.width * self.MAX_ROOM_SIZE_FACTOR)
        self.max_room_height = int(self.size.height * self.MAX_ROOM_SIZE_FACTOR)
        self.max_room_area = self.max_room_width * self.max_room_height * self.MAX_ROOM_AREA_FACTOR
        self.min_rooms_area = self.size.area * self.MIN_ROOMS_AREA_FACTOR
        self.max_rooms_distance = max(self.size) * self.MAX_ROOMS_DISTANCE_FACTOR

        self.rooms = []
        self.corridors = []

        self.connections = collections.defaultdict(set)
        self.distances = collections.defaultdict(list)

        self.init_rng(seed)

    def init_rng(self, seed):
        if seed is None:
            seed = uuid.uuid4()
        log.debug(f'LevelGenerator({self.size}) seed= {seed}')
        random.seed(seed)

    @property
    def level(self):
        if not self._level:
            self._level = GameMap.create(self.size, self.depth)
        return self._level

    def generate_room(self):
        size = Size(
            random.randint(self.MIN_ROOM_SIZE, self.max_room_width),
            random.randint(self.MIN_ROOM_SIZE, self.max_room_height)
        )
        position = Position(
            random.randint(1, self.level.width-size.width-1),
            random.randint(1, self.level.height-size.height-1),
        )
        return Room(position, size)

    def generate_rooms(self):
        # Generate rooms until 40% of level area is covered
        while sum(room.area for room in self.rooms) < self.min_rooms_area:
            room = self.generate_room()
            if room.area > self.max_room_area:
                continue
            if any(room.intersection(other) for other in self.rooms):
                continue
            self.rooms.append(room)

    def calc_room_distances(self):
        for room in self.rooms:
            for other in self.rooms:
                if other == room:
                    continue
                distance = room.center.distance(other.center)
                self.distances[room].append([distance, other])

    def get_vertical_corridors(self, room, other):
        corridors = []
        for x in room.horizontal_share(other):
            y = min(room.y2, other.y2)
            length = room.vertical_between(other)
            corridor = VerticalCorridor(Position(x, y), length)
            corridors.append(corridor)
        return corridors

    def get_horizontal_corridors(self, room, other):
        corridors = []
        for y in room.vertical_share(other):
            x = min(room.x2, other.x2)
            length = room.horizontal_between(other)
            corridor = HorizontalCorridor(Position(x, y), length)
            corridors.append(corridor)
        return corridors

    def connect_vertical(self, room, other):
        corridors = self.get_vertical_corridors(room, other)
        for corridor in random.sample(corridors, len(corridors)):
            if any(corridor.intersection(r) for r in self.rooms
               if not (r == room or r == other)):
                continue
            self.corridors.append(corridor)
            return corridor

    def connect_horizontal(self, room, other):
        corridors = self.get_horizontal_corridors(room, other)
        for corridor in random.sample(corridors, len(corridors)):
            if any(corridor.intersection(r) for r in self.rooms
               if not (r == room or r == other)):
                continue
            self.corridors.append(corridor)
            return corridor

    def connect(self, room, other):
        vertical_corridor = self.connect_vertical(room, other)
        horizontal_corridor = self.connect_horizontal(room, other)
        if vertical_corridor or horizontal_corridor:
            self.connections[room].add(other)
            self.connections[other].add(room)
            return vertical_corridor or horizontal_corridor

    def connect_room(self, room, rooms=None):
        rooms = rooms or self.rooms
        distances = sorted(self.distances[room], key=lambda e: e[0])
        connected = False
        for distance, other in distances:
            if other in self.connections[room]:
                continue
            if not other in rooms:
                continue
            if distance > self.max_rooms_distance:
                continue
            if self.connect(room, other):
                connected = True
                next_room_chance = 1/(len(self.connections[room])*5)
                if random.random() > next_room_chance:
                    break
                log.debug(f'Another corridor from: {room}')
        return connected

    def connect_rooms(self):
        for room in self.rooms:
            self.connect_room(room)

    def get_connections(self, room, connections=None):
        connections = connections or set()
        connections.add(room)
        for connected in self.connections[room]:
            if connected in connections:
                continue
            connections.update(self.get_connections(connected, connections))
        return connections

    def fix_connections(self, tries=1):
        connected = self.get_connections(self.rooms[0])
        disconnected = [room for room in self.rooms if not room in connected]
        if not disconnected:
            return []
        if tries > 10:
            return disconnected
        self.max_rooms_distance *= (1.+.1*tries)
        for room in random.sample(disconnected, len(disconnected)):
            log.debug(f'Fixing: {room}')
            if self.connect_room(room, rooms=connected):
                break
        tries += 1
        return self.fix_connections(tries)

    def fill(self, terrain):
        self.level.terrain[:] = terrain.id

    def dig_rooms(self, wall, floor):
        # Dig out rooms
        for room in self.rooms:
            room.set_walls(self.level, wall)
            room.dig_floor(self.level, floor)

    def dig_corridors(self, floor):
        for corridor in self.corridors:
            # NOTE: No set_walls for now since crossing corridors would be blocked!
            corridor.dig_floor(self.level, floor)

    def spawn_closed_door(self, position):
        closed_door = entities.create(self.ecs, entities.CLOSED_DOOR)
        entities.spawn(self.ecs, closed_door, self.level.id, position)

    def spawn_monster(self, position):
        monster = entities.create(self.ecs, entities.MONSTER)
        entities.spawn(self.ecs, monster, self.level.id, position)

    def spawn_entities(self):
        # Entities Spawning
        # Player in center of first room
        player = entities.create(self.ecs, entities.PLAYER)
        entities.spawn(self.ecs, player, self.level.id, self.rooms[0].center)

        # Doors
        for corridor in self.corridors:
            if corridor.length == 1:
                position = corridor.get_position(0)
                self.spawn_closed_door(position)
            elif corridor.length > 2:
                if random.random() < .25:
                    position = corridor.get_position(0)
                    self.spawn_closed_door(position)
                if random.random() < .25:
                    position = corridor.get_position(-1)
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
            monsters_num = random.randint(min_monsters_num, max_monsters_num)
            room_positions = list(room.inner.positions)
            monster_positions = set()
            for i in range(monsters_num):
                position = random.choice(room_positions)
                while position in monster_positions:
                    position = random.choice(room_positions)
                monster_positions.add(position)
                self.spawn_monster(position)


    def generate(self):
        self.generate_rooms()
        log.debug(f'Rooms: {len(self.rooms)}')

        self.calc_room_distances()

        self.connect_rooms()
        disconnected = self.fix_connections()
        if len(disconnected) > 1:
            raise ValueError(disconnected)

        self.fill(Terrain.STONE_WALL)
        self.dig_rooms(wall=Terrain.STONE_WALL, floor=Terrain.STONE_FLOOR)
        self.dig_corridors(floor=Terrain.STONE_FLOOR)

        self.spawn_entities()

        self.level.revealed[:] = 1
        return self.level


LevelGenerator = RoomsWithStraightCorridorsLevelGenerator


def generate_static_level(ecs, size):
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

