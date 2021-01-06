import collections
import logging
import random
import uuid

from . import entities
from .game_map import GameMap
from .geometry import Position, Size, Rectangle
from .terrain import Terrain


log = logging.getLogger(__name__)


SEED = None
#SEED = uuid.UUID( '137ad920-fd42-470a-a99c-6ed52b7c05b5' )


class OffsetedRectangle(Rectangle):

    INNER_OFFSET = Position.ZERO

    def __init__(self, position, size):
        self.inner = Rectangle(position, size)
        super().__init__(
            position-self.INNER_OFFSET,
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

    def horizontal_overlap(self, other):
        overlapping_x = (
            max(self.inner.x, other.inner.x),
            min(self.inner.x2, other.x2)
        )
        if overlapping_x[0] > overlapping_x[1]:
            return []
        return list(range(*overlapping_x))

    def vertical_overlap(self, other):
        overlapping_y = (
            max(self.inner.y, other.inner.y),
            min(self.inner.y2, other.y2)
        )
        if overlapping_y[0] > overlapping_y[1]:
            return []
        return list(range(*overlapping_y))

    def horizontal_spacing(self, other):
        min_x = min(self.x2, other.x2)
        max_x = max(self.inner.x, other.inner.x)
        return max_x-min_x

    def vertical_spacing(self, other):
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


class Generator:

    """Abstract Generator class. Use existing RNG or inits new using given seed."""

    def __init__(self, rng=None, seed=None):
        self.rng = rng or self.init_rng(seed)

    def init_rng(self, seed=None):
        """Init RNG with given seed, or generate new seed."""
        if seed is None:
            seed = uuid.uuid4()
        log.debug(f'Generator seed: {seed}')
        rng = random.Random(seed)
        return rng


class RoomGenerator(Generator):

    MIN_SIZE = 5    # Minimal width/height
    MAX_SIZE = 31   # Maximal width/height
    MAX_SIZE_FACTOR = 1.0   # Maximal width/height relative to area
    MAX_AREA_FACTOR = 1.0   # Maximal room area relative to area

    def __init__(
        self, rng,
        min_size=MIN_SIZE,
        max_size=MAX_SIZE,
        max_size_factor=MAX_SIZE_FACTOR,
        max_area_factor=MAX_AREA_FACTOR,
        area=None,
    ):
        super().__init__(rng)
        self.min_size = min_size
        self.max_size = max_size
        self.max_size_factor = max_size_factor
        self.max_area_factor = max_area_factor
        self._area = area
        self._max_size = self.get_max_size(area)

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, area):
        self._area = area
        self._max_size = self.get_max_size(area)

    def get_max_size(self, area):
        if not area:
            return None
        max_size = Size(
            min(self.max_size, int((area.width-2) * self.max_size_factor)),
            min(self.max_size, int((area.height-2) * self.max_size_factor))
        )
        return max_size

    def generate(self, area=None):
        """Generate random room."""
        if area is not None:
            max_size = self.get_max_size(area)
        else:
            area = self.area
            max_size = self._max_size
        max_area = max_size.area * self.max_area_factor

        size = max_size
        while size.area > max_area:
            size = Size(
                self.rng.randint(self.min_size, max_size.width),
                self.rng.randint(self.min_size, max_size.height)
            )
        position = Position(
            self.rng.randint(area.x+1, area.x+area.width-size.width-1),
            self.rng.randint(area.y+1, area.y+area.height-size.height-1),
        )
        return Room(position, size)


class RoomsGenerator(Generator):

    def __init__(self, rng):
        super().__init__(rng)
        self.rooms = []

    def generate(self):
        return self.rooms


class RandomlyPlacedRoomsGenerator(RoomsGenerator):

    MAX_ROOM_SIZE_FACTOR = .45
    MAX_ROOM_AREA_FACTOR = .30

    MIN_ROOMS_AREA_FACTOR = .40

    """Place non-overlapping rooms randomly until area big enough is covered."""

    def __init__(self, rng, level):
        super().__init__(rng)

        self.room_generator = RoomGenerator(
            self.rng,
            max_size_factor=self.MAX_ROOM_SIZE_FACTOR,
            max_area_factor=self.MAX_ROOM_AREA_FACTOR,
            area=level,
        )

        self.min_rooms_area = level.area * self.MIN_ROOMS_AREA_FACTOR

    def generate(self):
        """Generate rooms covering at least min_rooms_area of the level area."""
        while sum(room.area for room in self.rooms) < self.min_rooms_area:
            room = self.room_generator.generate()
            if any(room.intersection(other) for other in self.rooms):
                continue
            self.rooms.append(room)

        log.debug(f'Rooms: {len(self.rooms)}')
        return self.rooms


class GridRoomsGenerator(RoomsGenerator):

    MIN_ROOM_SIZE = 4
    MAX_ROOM_SIZE_FACTOR = .95
    MAX_ROOM_AREA_FACTOR = .85

    """Place rooms using grid with cells of approximately the same size."""

    def __init__(self, rng, level, grid):
        super().__init__(rng)

        self.room_generator = RoomGenerator(
            self.rng,
            min_size=self.MIN_ROOM_SIZE,
            max_size_factor=self.MAX_ROOM_SIZE_FACTOR,
            max_area_factor=self.MAX_ROOM_AREA_FACTOR,
        )

        self.level = level
        self.grid = grid

    def get_cell_sizes(self, total_size, cells_num):
        """Return list of widths/heights for each cell in grid."""
        # total_size-1 because we leave out right and bottom edge for room walls
        even_size = (total_size-1) // cells_num
        sizes = []
        for i in range(cells_num):
            sizes.append(even_size)
        # Randomly increase size of cells so total_size is used
        rest = (total_size-1) % cells_num
        for i in self.rng.sample(range(len(sizes)), rest):
            sizes[i] += 1
        return sizes

    def generate(self):
        widths = self.get_cell_sizes(self.level.width, self.grid.width)
        heights = self.get_cell_sizes(self.level.height, self.grid.height)

        x = 0
        for width in widths:
            y = 0
            for height in heights:
                # Size with width/height+1 because we want rooms to touch
                area = Rectangle(Position(x, y), Size(width+1, height+1))
                room = self.room_generator.generate(area)
                self.rooms.append(room)
                y += height
            x += width

        return self.rooms


class StraightCorridorsGenerator(Generator):

    MAX_CORRIDOR_DISTANCE_FACTOR = .30

    def __init__(self, rng, size):
        super().__init__(rng)

        self.rooms = []
        self.corridors = []

        self.max_corridor_distance = max(size) * self.MAX_CORRIDOR_DISTANCE_FACTOR

        self.connections = collections.defaultdict(set)
        self.distances = collections.defaultdict(list)

    def calc_room_distances(self):
        """Calculate distances between rooms."""
        self.distances.clear()
        for room in self.rooms:
            for other in self.rooms:
                if other == room:
                    continue
                distance = room.center.distance(other.center)
                self.distances[room].append([distance, other])

    def get_vertical_corridors(self, room, other):
        """Return all possible vertical corridors connecting to other room."""
        corridors = []
        for x in room.horizontal_overlap(other):
            y = min(room.y2, other.y2)
            length = room.vertical_spacing(other)
            corridor = VerticalCorridor(Position(x, y), length)
            corridors.append(corridor)
        return corridors

    def get_horizontal_corridors(self, room, other):
        """Return all possible horizontal corridors connecting to other room."""
        corridors = []
        for y in room.vertical_overlap(other):
            x = min(room.x2, other.x2)
            length = room.horizontal_spacing(other)
            corridor = HorizontalCorridor(Position(x, y), length)
            corridors.append(corridor)
        return corridors

    def select_corridor(self, corridors, rooms):
        """Select random corridor that do NOT intersect with given rooms."""
        for corridor in self.rng.sample(corridors, len(corridors)):
            # Do NOT create corridors intersecting with rooms
            if any(corridor.intersection(r) for r in rooms):
                continue
            return corridor

    def connect_vertical(self, room, other):
        """Try creating vertical corridor by randomly checking possible connections."""
        corridors = self.get_vertical_corridors(room, other)
        rooms = set(self.rooms) - {room, other}
        return self.select_corridor(corridors, rooms)

    def connect_horizontal(self, room, other):
        """Try creating horizontal corridor by randomly checking possible connections."""
        corridors = self.get_horizontal_corridors(room, other)
        rooms = set(self.rooms) - {room, other}
        return self.select_corridor(corridors, rooms)

    def connect(self, room, other):
        """Try creating vertical or horizontal corridor to other room."""
        vertical_corridor = self.connect_vertical(room, other)
        horizontal_corridor = self.connect_horizontal(room, other)
        corridor = vertical_corridor or horizontal_corridor
        if corridor:
            self.corridors.append(corridor)
            self.connections[room].add(other)
            self.connections[other].add(room)
            return corridor

    def connect_room(self, room, rooms=None):
        """Try connecting given room with closest room, not yet connected with it."""
        rooms = rooms or self.rooms
        distances = sorted(self.distances[room], key=lambda e: e[0])
        connected = False
        for distance, other in distances:
            if other in self.connections[room]:
                continue
            if not other in rooms:
                continue
            if distance > self.max_corridor_distance:
                continue
            if self.connect(room, other):
                connected = True
                # There's small chance for creating extra connection from this room
                next_room_chance = 1/(len(self.connections[room])*5)
                if self.rng.random() > next_room_chance:
                    break
                log.debug(f'Another corridor from: {room}')
        return connected

    def get_connections(self, room, connections=None):
        """Return recursively all connected rooms with given room."""
        connections = connections or set()
        connections.add(room)
        for connected in self.connections[room]:
            if connected in connections:
                continue
            connections.update(self.get_connections(connected, connections))
        return connections

    def fix_connections(self, tries=1, max_tries=10):
        """Check for all disconnected rooms, and try to fix them."""
        # Get all rooms that are accessible from first room
        connected = self.get_connections(self.rooms[0])
        # Get rooms that are NOT connected and not accessible
        disconnected = [room for room in self.rooms if not room in connected]
        if not disconnected:
            # Nothing to fix here, all rooms are nicely connected
            return []
        # On each try increase max_corridor_distance, on last try it will be twice as big
        self.max_corridor_distance *= (1.+.1*tries)
        if tries > max_tries:
            return disconnected
        # Try to connect disconnected rooms with connected ones
        for room in self.rng.sample(disconnected, len(disconnected)):
            log.debug(f'Fixing: {room}')
            if self.connect_room(room, rooms=connected):
                break
        tries += 1
        return self.fix_connections(tries)

    def generate(self, rooms):
        self.rooms = rooms
        self.calc_room_distances()

        for room in self.rooms:
            self.connect_room(room)

        # Check for rooms that are not connected with others
        disconnected = self.fix_connections()
        if len(disconnected) > 1:
            raise ValueError(disconnected)

        return self.corridors


class RoomsLevelGenerator(Generator):

    def __init__(self, ecs, size, depth=0, seed=SEED):
        super().__init__(seed=seed)

        self.ecs = ecs

        self.size = size
        self.depth = depth
        self.level = GameMap.create(self.size, self.depth)

        self.rooms = []
        self.rooms_generator = None

        self.corridors = []
        self.corridors_generator = None

    def generate_rooms(self):
        self.rooms = self.rooms_generator.generate()

    def generate_corridors(self):
        self.corridors = self.corridors_generator.generate(self.rooms)

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
        self.generate_corridors()

        self.fill(Terrain.STONE_WALL)
        self.dig_rooms(wall=Terrain.STONE_WALL, floor=Terrain.STONE_FLOOR)
        self.dig_corridors(floor=Terrain.STONE_FLOOR)

        self.spawn_entities()

        self.level.revealed[:] = 1
        return self.level


class RoomsWithStraightCorridorsLevelGenerator(RoomsLevelGenerator):

    """LevelGenerator creating random rooms connected with straight corridors."""

    def __init__(self, ecs, size, depth=0, seed=SEED):
        super().__init__(ecs, size, depth, seed=seed)

        #self.rooms_generator = RandomlyPlacedRoomsGenerator(self.rng, self.level)
        self.rooms_generator = GridRoomsGenerator(self.rng, self.level, Size(4, 3))
        self.corridors_generator = StraightCorridorsGenerator(self.rng, self.level.size)

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
                self.spawn_closed_door(position)
            elif corridor.length > 2:
                # Never spawn doors in corridors with length == 2
                # Otherwise there's 25% chance of door on each end of corridor
                if self.rng.random() < .25:
                    position = corridor.get_position(0)
                    self.spawn_closed_door(position)
                if self.rng.random() < .25:
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

