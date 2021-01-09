import collections
import logging

from ..geometry import Position, Size, Rectangle

from .core import Generator
from .core import Room


log = logging.getLogger(__name__)


class RoomGenerator(Generator):

    """Generate single Room with random size and position on given area."""

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
            min(self.max_size, int((area.width-Room.OFFSET.x) * self.max_size_factor)),
            min(self.max_size, int((area.height-Room.OFFSET.y) * self.max_size_factor))
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
            self.rng.randint(area.x+Room.OFFSET.x, area.x+area.width-size.width),
            self.rng.randint(area.y+Room.OFFSET.y, area.y+area.height-size.height),
        )
        return Room(position, size)


class RoomsGenerator(Generator):

    """Generate Rooms and calculate distances between them."""

    def __init__(self, rng):
        super().__init__(rng)
        self.rooms = []

    def calc_room_distances(self, room):
        """Calculate distances from given room."""
        return {}

    def calc_distances(self):
        """Calculate distances between all rooms."""
        distances = collections.defaultdict(list)
        for room in self.rooms:
            if room is None:
                continue
            room_distances = self.calc_room_distances(room)
            for distance, others in room_distances.items():
                distances[room].append([distance, others])
        return distances

    def generate_rooms(self):
        raise NotImplementedError()

    def generate(self):
        self.generate_rooms()
        distances = self.calc_distances()
        return distances


class RandomlyPlacedRoomsGenerator(RoomsGenerator):

    """Place non-overlapping rooms randomly until area big enough is covered."""

    MAX_ROOM_SIZE_FACTOR = .45
    MAX_ROOM_AREA_FACTOR = .30

    MIN_ROOMS_AREA_FACTOR = .40

    def __init__(self, rng, level):
        super().__init__(rng)

        rooms_area = Rectangle(
            Position.ZERO,
            Size(level.width-Room.OFFSET.x, level.height-Room.OFFSET.y)
        )
        self.room_generator = RoomGenerator(
            self.rng,
            max_size_factor=self.MAX_ROOM_SIZE_FACTOR,
            max_area_factor=self.MAX_ROOM_AREA_FACTOR,
            area=rooms_area,
        )

        self.min_rooms_area = level.area * self.MIN_ROOMS_AREA_FACTOR

    def calc_room_distances(self, room):
        """Calculate distances from given room."""
        room_distances = collections.defaultdict(set)
        for other in self.rooms:
            if other == room:
                continue
            distance = room.center.distance(other.center)
            room_distances[distance].add(other)
        return room_distances

    def generate_rooms(self):
        """Generate rooms covering at least min_rooms_area of the level area."""
        while sum(room.area for room in self.rooms) < self.min_rooms_area:
            room = self.room_generator.generate()
            if any(room.intersection(other) for other in self.rooms):
                continue
            self.rooms.append(room)

        log.debug(f'Rooms: {len(self.rooms)}')
        return self.rooms


class GridRoomsGenerator(RoomsGenerator):

    """Place rooms using grid with cells of approximately the same size."""

    MIN_ROOM_SIZE = 4
    MAX_ROOM_SIZE_FACTOR = .95
    MAX_ROOM_AREA_FACTOR = .85

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

    def calc_room_distances(self, room):
        """Calculate distances from given room."""
        room_distances = collections.defaultdict(set)
        room_idx = self.rooms.index(room)
        width = self.grid.width
        # cell_length to get tiles-based distances instead of grid cell-based distances
        cell_length = sum([self.level.width//self.grid.width, self.level.height//self.grid.height])//2
        for other_idx, other in enumerate(self.rooms):
            if other is None:
                continue
            if other == room:
                continue
            distance = abs(other_idx%width-room_idx%width) + abs(other_idx//width-room_idx//width)
            room_distances[distance*cell_length].add(other)
        return room_distances

    def get_cell_sizes(self, total_size, cells_num):
        """Return list of widths/heights for each cell in grid."""
        # total_size-1 because we leave out right and bottom edge for room walls
        even_size = (total_size) // cells_num
        sizes = []
        for i in range(cells_num):
            sizes.append(even_size)
        # Randomly increase size of cells so total_size is used
        rest = (total_size) % cells_num
        for i in self.rng.sample(range(len(sizes)), rest):
            sizes[i] += 1
        return sizes

    def generate_rooms(self):
        # Calculate widths and heights for all grid cells
        widths = self.get_cell_sizes(self.level.width-Room.OFFSET.x, self.grid.width)
        heights = self.get_cell_sizes(self.level.height-Room.OFFSET.y, self.grid.height)

        # Generate all rooms in grid
        y = 0
        for height in heights:
            x = 0
            for width in widths:
                # Size with width/height+1 because we want rooms to touch
                area = Rectangle(Position(x, y), Size(width, height))
                room = self.room_generator.generate(area)
                self.rooms.append(room)
                x += width
            y += height

        # Randomly remove room(s)
        remove_room_chance = .6
        while True:
            if self.rng.random() < remove_room_chance:
                remove_idx = self.rng.randrange(0, len(self.rooms))
                log.debug(f'Removing room: {remove_idx}')
                self.rooms[remove_idx] = None
                remove_room_chance /= 2
            else:
                break

        return self.rooms

