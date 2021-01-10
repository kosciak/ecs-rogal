import collections
import logging
import math

from .core import Generator
from .corridors import StraightCorridorGenerator, ZShapeCorridorGenerator, MixedCorridorGenerator


log = logging.getLogger(__name__)


class RoomsConnector(Generator):

    """Connect rooms."""

    MAX_CONNECTION_DISTANCE_FACTOR = .30

    def __init__(self, rng, size):
        super().__init__(rng)

        self.distances = collections.defaultdict(list)
        self.rooms = []
        self.corridors = []

        self.corridor_generator = MixedCorridorGenerator([
            (StraightCorridorGenerator(self.rng), 1),
            (ZShapeCorridorGenerator(self.rng), 6),
        ], self.rng)

        # TODO: Different RoomsGenerators might use different distance bases
        #       euclidean distance, grid distance, BSP related distance, etc
        self.max_connection_distance = max(size) * self.MAX_CONNECTION_DISTANCE_FACTOR

    def set_distances(self, distances):
        self.distances = distances
        self.rooms = list(self.distances.keys())
        self.corridors = []

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

    def nearest_rooms(self, room):
        """Yield (distance, other) pairs from nearest to furthest room."""
        for distance, others in sorted(self.distances[room]):
            for other in self.rng.sample(others, len(others)):
                yield distance, other

    def generate_corridors(self, room, other):
        rooms = set(self.rooms) - {room, other}
        for corridors in self.corridor_generator.generate(room, other):
            if self.is_corridor_valid(corridors, rooms):
                return corridors

    def is_connection_valid(self, room, other, distance, include_rooms=None):
        """Return True if connection between room and other can be created."""
        if include_rooms is None:
            include_rooms = self.rooms
        if other in room.connected_rooms:
            # Already connected to this room
            return False
        if not other in include_rooms:
            # No need to connect to this room
            return False
        if distance > self.max_connection_distance:
            # Room too far
            return False
        return True

    def connect_room(self, room, include_rooms=None):
        """Try connecting given room with closest valid room, not yet connected with it."""
        if include_rooms is None:
            include_rooms = self.rooms
        for distance, other in self.nearest_rooms(room):
            if not self.is_connection_valid(room, other, distance, include_rooms):
                continue
            corridors = self.generate_corridors(room, other)
            if corridors:
                self.corridors.extend(corridors)
                corridors[0].allow_door(0)
                corridors[-1].allow_door(-1)
                room.connected_rooms.add(other)
                other.connected_rooms.add(room)
                return other
        return None

    def connect(self, distances):
        self.set_distances(distances)

        log.error('Implement me!')

        return self.corridors


class RandomToNearestRoomsConnector(RoomsConnector):

    def connect(self, distances):
        self.set_distances(distances)

        # Try to connect each room with nearest neighbour
        for room in self.rng.sample(self.rooms, len(self.rooms)):
            other = self.connect_room(room)
            log.debug(f'Connected: {self.rooms.index(room)} -> {other and self.rooms.index(other)}')

        # There's small chance for creating additional connections from each room
        for room in self.rng.sample(self.rooms, len(self.rooms)):
            if room.connected_rooms:
                next_room_chance = 1/(len(room.connected_rooms)*5)
            else:
                next_room_chance = .9
            if self.rng.random() > next_room_chance:
                continue
            log.debug(f'Extra from: {self.rooms.index(room)}')
            other = self.connect_room(room)
            log.debug(f'Connected: {self.rooms.index(room)} -> {other and self.rooms.index(other)}')

        # Check for rooms that are not connected with others
        disconnected = self.fix_connections()
        if len(disconnected) > 1:
            raise ValueError(disconnected)

        return self.corridors


class FollowToNearestRoomsConnector(RoomsConnector):

    """Connection algorithm similar to original Rogue.

    See: https://web.archive.org/web/20131025132021/http://kuoi.org/~kamikaze/GameDesign/art07_rogue_dungeon.php

    """

    def connect(self, distances):
        self.set_distances(distances)

        # Randomly choose starting room, and connect with one of not connected
        room = self.rng.choice(self.rooms)
        while room:
            unconnected = {r for r in self.rooms if not r.connected_rooms}
            other = self.connect_room(room, unconnected)
            log.debug(f'Connected: {self.rooms.index(room)} -> {other and self.rooms.index(other)}')
            # Use this room as new starting one
            room = other

        # Connect rooms that are not yet connected to connected ones
        distance_factor = 2
        unconnected = [room for room in self.rooms if not room.connected_rooms]
        tries = len(unconnected)
        log.debug(f'Unconnected: {len(unconnected)}')
        while unconnected:
            if tries == 0:
                self.max_connection_distance *= distance_factor
                distance_factor = 1
            tries -= 1
            room = self.rng.choice(unconnected)
            connected = {r for r in self.rooms if r.connected_rooms}
            other = self.connect_room(room, connected)
            log.debug(f'Connected: {self.rooms.index(room)} -> {other and self.rooms.index(other)}')
            unconnected = [r for r in self.rooms if not r.connected_rooms]

        # Some extra connections
        self.max_connection_distance *= distance_factor
        extra_connections_num = self.rng.randint(1, int(math.sqrt(len(self.rooms))))
        log.debug(f'Extra connections: {extra_connections_num}')
        for room in self.rng.sample(self.rooms, extra_connections_num):
            other = self.connect_room(room)
            log.debug(f'Connected: {self.rooms.index(room)} -> {other and self.rooms.index(other)}')

        # Check for rooms that are not connected with others
        disconnected = self.fix_connections()
        if len(disconnected) > 1:
            raise ValueError(disconnected)

        return self.corridors

