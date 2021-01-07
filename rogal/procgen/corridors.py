import collections
import logging

from ..geometry import Position

from .core import Generator
from .core import VerticalCorridor, HorizontalCorridor


log = logging.getLogger(__name__)


class CorridorGenerator(Generator):

    """Generate random corridor(s) connecting two rooms."""

    def generate_vertical(self, room, other):
        yield from ()

    def generate_horizontal(self, room, other):
        yield from ()

    def generate(self, room, other):
        """Try creating vertical or horizontal corridor to other room."""
        generator_fns = [
            self.generate_vertical,
            self.generate_horizontal,
        ]
        for generator_fn in self.rng.sample(generator_fns, len(generator_fns)):
            yield from generator_fn(room, other)


class StraightCorridorGenerator(CorridorGenerator):

    """Generate straight corridor. Works only if two rooms overlaps on a plane."""

    def generate_vertical(self, room, other):
        """Yield all possible vertical corridors connecting to other room."""
        length = room.vertical_spacing(other)
        y = min(room.y2, other.y2)
        overlaps = room.horizontal_overlap(other)
        for x in self.rng.sample(overlaps, len(overlaps)):
            corridor = VerticalCorridor(Position(x, y), length)
            yield (corridor, )

    def generate_horizontal(self, room, other):
        """Yield all possible horizontal corridors connecting to other room."""
        length = room.horizontal_spacing(other)
        x = min(room.x2, other.x2)
        overlaps = room.vertical_overlap(other)
        for y in self.rng.sample(overlaps, len(overlaps)):
            corridor = HorizontalCorridor(Position(x, y), length)
            yield (corridor, )


class ZShapeCorridorGenerator(StraightCorridorGenerator):

    """Generate Z-shaped corridor: vertical-horizontal-vertical or horizontal-vertical-horizontal."""

    def generate_vertical(self, room, other):
        """Yield possible vertical corridors connecting to other room."""
        length = room.vertical_spacing(other)
        if length < 3:
            yield from super().generate_vertical(room, other)
            return
        y = min(room.y2, other.y2)
        y2 = y + length
        y_break = self.rng.randrange(y+1, y2-1)
        count = 5 # How many variations to try
        while count:
            count -= 1
            if y == room.y2:
                x = self.rng.randrange(room.inner.x, room.x2)
                x2 = self.rng.randrange(other.inner.x, other.x2)
            else:
                x = self.rng.randrange(other.inner.x, other.x2)
                x2 = self.rng.randrange(room.inner.x, room.x2)
            yield (
                VerticalCorridor(Position(x, y), y_break-y+1),
                HorizontalCorridor(Position(min(x, x2), y_break), abs(x2-x)),
                VerticalCorridor(Position(x2, y_break), y2-y_break),
            )

    def generate_horizontal(self, room, other):
        """Yield possible horizontal corridors connecting to other room."""
        length = room.horizontal_spacing(other)
        if length < 3:
            yield from super().generate_horizontal(room, other)
            return
        x = min(room.x2, other.x2)
        x2 = x + length
        count = 5 # How many variations to try
        while count:
            count -= 1
            x_break = self.rng.randrange(x+1, x2-1)
            if x == room.x2:
                y = self.rng.randrange(room.inner.y, room.y2)
                y2 = self.rng.randrange(other.inner.y, other.y2)
            else:
                y = self.rng.randrange(other.inner.y, other.y2)
                y2 = self.rng.randrange(room.inner.y, room.y2)
            yield (
                HorizontalCorridor(Position(x, y), x_break-x+1),
                VerticalCorridor(Position(x_break, min(y, y2)), abs(y2-y)),
                HorizontalCorridor(Position(x_break, y2), x2-x_break),
            )


class RoomsConnector(Generator):

    """Connect rooms."""

    MAX_CONNECTION_DISTANCE_FACTOR = .30

    def __init__(self, rng, size):
        super().__init__(rng)

        self.rooms = []
        self.corridors = []

        #self.corridor_generator = StraightCorridorGenerator(self.rng)
        self.corridor_generator = ZShapeCorridorGenerator(self.rng)

        self.max_connection_distance = max(size) * self.MAX_CONNECTION_DISTANCE_FACTOR

        self.distances = collections.defaultdict(list)

    def get_connections(self, room, connections=None):
        """Return recursively all connected rooms with given room."""
        connections = connections or set()
        connections.add(room)
        for connected in room.connected_rooms:
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
        # On each try increase max_connection_distance, on last try it will be twice as big
        self.max_connection_distance *= (1.+.1*tries)
        if tries > max_tries:
            return disconnected
        # Try to connect disconnected rooms with connected ones
        for room in self.rng.sample(disconnected, len(disconnected)):
            log.debug(f'Fixing: {room}')
            other = self.connect_room(room, rooms=connected)
            if other:
                break
        tries += 1
        return self.fix_connections(tries)

    def is_corridor_valid(self, corridors, rooms):
        """Return True if given corridor can be craeted."""
        for corridor in corridors:
            # Do NOT create corridors intersecting with rooms
            if any(corridor.intersection(r) for r in rooms):
                return False
            # Do NOT create corridors intersecting with other corridors on same vertical/horizontal plane
            if any(corridor.intersection(c) for c in self.corridors
                   if corridor.is_horizontal == c.is_horizontal):
                return False
        return True

    def nearest_rooms(self, room, rooms=None):
        """Yield (distance, other) pairs from nearest to furthest room."""
        rooms = rooms or self.rooms
        for distance, others in sorted(self.distances[room]):
            for other in self.rng.sample(others, len(others)):
                yield distance, other

    def connect(self, room, other):
        rooms = set(self.rooms) - {room, other}
        for corridors in self.corridor_generator.generate(room, other):
            if self.is_corridor_valid(corridors, rooms):
                return corridors

    def is_connection_valid(self, room, distance, other, rooms=None):
        """Return True if connection between room and other can be created."""
        rooms = rooms or self.rooms
        if other in room.connected_rooms:
            # Already connected to this room
            return False
        if not other in rooms:
            # No need to connect to this room
            return False
        if distance > self.max_connection_distance:
            # Room too far
            return False
        return True

    def connect_room(self, room, rooms=None):
        """Try connecting given room with closest room, not yet connected with it."""
        rooms = rooms or self.rooms
        for distance, other in self.nearest_rooms(room, rooms):
            if not self.is_connection_valid(room, distance, other, rooms):
                continue
            corridors = self.connect(room, other)
            if corridors:
                self.corridors.extend(corridors)
                corridors[0].allow_door(0)
                corridors[-1].allow_door(-1)
                room.connected_rooms.add(other)
                other.connected_rooms.add(room)
                return other
        return None

    def generate(self, distances):
        self.distances = distances
        self.rooms = list(self.distances.keys())

        # Try to connect each room with nearest neighbour
        for room in self.rng.sample(self.rooms, len(self.rooms)):
            other = self.connect_room(room)

        # There's small chance for creating additional connections from each room
        for room in self.rng.sample(self.rooms, len(self.rooms)):
            if room.connected_rooms:
                next_room_chance = 1/(len(room.connected_rooms)*5)
            else:
                next_room_chance = .9
            if self.rng.random() > next_room_chance:
                continue
            log.debug(f'Another corridor from: {room}')
            other = self.connect_room(room)

        # Check for rooms that are not connected with others
        disconnected = self.fix_connections()
        if len(disconnected) > 1:
            raise ValueError(disconnected)

        return self.corridors

