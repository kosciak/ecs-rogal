import collections
import logging

from ..geometry import Position, Size, Rectangle

from .core import Generator, Digable
from .bsp import BSPGenerator


log = logging.getLogger(__name__)


class Room(Digable):

    """Rectangular room.

    Left and top border are considered walls, so rooms can share walls with each other when adjecent.

    Room with Size(5, 3) has inner floor area of Size(4, 2) with offset (1, 1)

    #####
    #....
    #....

    """

    OFFSET = Position(1, 1)

    def __init__(self, position, size):
        super().__init__(position, size)
        self.connected_rooms = []

    def add_connected_room(self, other):
        if not other in self.connected_rooms:
            self.connected_rooms.append(other)

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
        level.terrain[self.x:self.x2+self.OFFSET.x, self.y:self.y2+self.OFFSET.y] = wall


class RoomGenerator(Generator):

    """Generate single Room with random size and position on given area."""

    MIN_SIZE = 5    # Minimal width/height
    MAX_SIZE = 25   # Maximal width/height
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
            min(self.max_size, int((area.width-Room.OFFSET.x) * self.max_size_factor)),
            min(self.max_size, int((area.height-Room.OFFSET.y) * self.max_size_factor))
        )
        return max_size

    def get_size(self, max_size, max_area, tries=50):
        if tries <= 0:
            return None
        if max_size.width < self.min_size:
            return None
        if max_size.height < self.min_size:
            return None

        size = Size(
            self.rng.randint(self.min_size, max_size.width),
            self.rng.randint(self.min_size, max_size.height)
        )

        if size.area > max_area:
            return self.get_size(max_size, max_area, tries-1)

        return size

    def generate(self, area=None):
        """Generate random room."""
        if area is not None:
            max_size = self.get_max_size(area)
        else:
            area = self.area
            max_size = self._max_size
        max_area = max_size.area * self.max_area_factor

        size = self.get_size(max_size, max_area)
        if size is None:
            return None

        position = Position(
            self.rng.randint(area.x+Room.OFFSET.x, area.x+area.width-size.width),
            self.rng.randint(area.y+Room.OFFSET.y, area.y+area.height-size.height),
        )
        return Room(position, size)


class RoomsGenerator(Generator):

    """Generate Rooms and calculate distances between them."""

    MIN_ROOM_SIZE = 4
    MAX_ROOM_SIZE_FACTOR = 1.0
    MAX_ROOM_AREA_FACTOR = 1.0

    def __init__(self, rng, level):
        super().__init__(rng)

        self.level = level
        self.rooms_area = Rectangle(
            Position.ZERO,
            Size(level.width-Room.OFFSET.x, level.height-Room.OFFSET.y)
        )
        self.rooms = []
        self._room_generator = None

    def init_room_generator(self):
        room_generator = RoomGenerator(
            self.rng,
            min_size=self.MIN_ROOM_SIZE,
            max_size_factor=self.MAX_ROOM_SIZE_FACTOR,
            max_area_factor=self.MAX_ROOM_AREA_FACTOR,
        )
        return room_generator

    @property
    def room_generator(self):
        if self._room_generator is None:
            self._room_generator = self.init_room_generator()
        return self._room_generator

    def clear(self):
        self.rooms = []

    def generate_room(self, area=None):
        room = self.room_generator.generate(area)
        return room

    def calc_room_distances(self, room):
        """Calculate distances from given room.

        Default implementation uses euclidean distance betwenn room centers.

        """
        room_distances = {}

        for other in self.rooms:
            if other is None:
                continue
            if other == room:
                continue
            distance = int(room.center.distance(other.center)//5)
            room_distances[other] = distance

        return room_distances

    def calc_rooms_distances(self):
        """Calculate distances between all rooms."""
        rooms_distances = collections.defaultdict(list)
        for room in self.rooms:
            if room is None:
                continue
            room_distances = self.calc_room_distances(room)
            distances = collections.defaultdict(list)
            for other, distance in room_distances.items():
                distances[distance].append(other)
            for distance, others in distances.items():
                rooms_distances[room].append([distance, others])
        return rooms_distances

    def rooms_distances_stats(self, rooms_distances):
        distance_counts = collections.Counter()
        for room, room_distances in rooms_distances.items():
            for distance, other in room_distances:
                distance_counts[distance] += 1
        for distance in sorted(distance_counts.keys()):
            count = distance_counts[distance]
            print(f'{distance} - {count}')

    def generate_rooms(self):
        raise NotImplementedError()

    def generate(self):
        self.clear()
        self.rooms = self.generate_rooms()
        rooms_distances = self.calc_rooms_distances()
        # self.rooms_distances_stats(rooms_distances)
        return rooms_distances


class RandomlyPlacedRoomsGenerator(RoomsGenerator):

    """Place non-overlapping rooms randomly until area big enough is covered."""

    MIN_ROOM_SIZE = 5
    MAX_ROOM_SIZE_FACTOR = .45
    MAX_ROOM_AREA_FACTOR = .30

    MIN_ROOMS_AREA_FACTOR = .40

    def __init__(self, rng, level):
        super().__init__(rng, level)

        self.min_rooms_area = level.area * self.MIN_ROOMS_AREA_FACTOR

    def init_room_generator(self):
        room_generator = RoomGenerator(
            self.rng,
            min_size=self.MIN_ROOM_SIZE,
            max_size_factor=self.MAX_ROOM_SIZE_FACTOR,
            max_area_factor=self.MAX_ROOM_AREA_FACTOR,
            area=self.rooms_area,
        )
        return room_generator

    def generate_rooms(self):
        """Generate rooms covering at least min_rooms_area of the level area."""
        rooms = []

        while sum(room.area for room in rooms) < self.min_rooms_area:
            room = self.generate_room()
            if any(room.intersection(other) for other in rooms):
                continue
            log.debug(f'Room: {len(rooms):2d} - {room}')
            rooms.append(room)

        log.debug(f'Rooms: {len(rooms)}')
        return rooms


class GridRoomsGenerator(RoomsGenerator):

    """Place rooms using grid with cells of approximately the same size."""

    MIN_ROOM_SIZE = 4
    MAX_ROOM_SIZE_FACTOR = .95
    MAX_ROOM_AREA_FACTOR = .85

    def __init__(self, rng, level, grid=None):
        super().__init__(rng, level)

        if grid is None:
            grid = Size(
                level.width//18,
                level.height//11,
            )
        self.grid = grid

    def calc_room_distances(self, room):
        """Calculate distances from given room."""
        room_distances = {}

        room_idx = self.rooms.index(room)
        width = self.grid.width
        for other_idx, other in enumerate(self.rooms):
            if other is None:
                continue
            if other == room:
                continue
            distance = abs(other_idx%width-room_idx%width) + abs(other_idx//width-room_idx//width)
            room_distances[other] = distance

        return room_distances

    def get_cell_sizes(self, length, cells_num):
        """Return list of widths/heights for each cell in grid."""
        even_size = (length) // cells_num
        sizes = []
        for i in range(cells_num):
            sizes.append(even_size)
        # Randomly increase size of cells so length is used
        rest = (length) % cells_num
        for i in self.rng.sample(range(len(sizes)), rest):
            sizes[i] += 1
        return sizes

    def generate_rooms(self):
        rooms = []

        # Calculate widths and heights for all grid cells
        widths = self.get_cell_sizes(self.rooms_area.width, self.grid.width)
        heights = self.get_cell_sizes(self.rooms_area.height, self.grid.height)

        # Generate all rooms in grid
        y = 0
        for height in heights:
            x = 0
            for width in widths:
                # Size with width/height+1 because we want rooms to touch
                area = Rectangle(Position(x, y), Size(width, height))
                room = self.generate_room(area)
                log.debug(f'Room: {len(rooms):2d} - {room}')
                rooms.append(room)
                x += width
            y += height

        # Randomly remove room(s)
        remove_room_chance = .6
        while True:
            if self.rng.random() < remove_room_chance:
                remove_idx = self.rng.randrange(len(rooms))
                log.debug(f'Removing room: {remove_idx}')
                rooms[remove_idx] = None
                remove_room_chance /= 2
            else:
                break

        return rooms

    def __repr__(self):
        return f'<{self.__class__.__name__} grid={self.grid}>'


class BSPRoomsGenerator(RoomsGenerator):

    MIN_ROOM_SIZE = 5
    MAX_ROOM_SIZE_FACTOR = .95
    MAX_ROOM_AREA_FACTOR = .85

    def __init__(self, rng, level, split_depth=None):
        super().__init__(rng, level)

        if split_depth is None:
            split_depth = level.width//18
        self.split_depth = split_depth
        self.bsp_generator = BSPGenerator(
            self.rng,
            self.rooms_area.position, self.rooms_area.size,
            min_size=int(self.MIN_ROOM_SIZE*1.5),
        )
        self.bsp_tree = None
        self.room_nodes = {}

    def clear(self):
        super().clear()
        self.room_nodes.clear()

    def calc_room_distances(self, room):
        """Calculate distances from given room."""
        room_distances = {}

        room_node = self.room_nodes[room]
        for other in self.rooms:
            if other == room:
                continue
            if other is None:
                continue
            other_node = self.room_nodes[other]
            distance = room_node.distance(other_node)
            room_distances[other] = distance

        return room_distances

    def generate_rooms(self):
        rooms = []

        self.bsp_tree = self.bsp_generator.generate(self.split_depth)
        for node in self.bsp_tree.leaves():
            room = self.generate_room(node)
            if room is None:
                continue
            log.debug(f'Room: {len(rooms):2d} - {room}')
            rooms.append(room)
            self.room_nodes[room] = node

        return rooms

