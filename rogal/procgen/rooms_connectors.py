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

        self.rooms_distances = collections.defaultdict(list)
        self.rooms = []
        self.corridors = []

        self.corridor_generator = MixedCorridorGenerator([
            (StraightCorridorGenerator(self.rng), 1),
            (ZShapeCorridorGenerator(self.rng), 6),
        ], self.rng)

        # self.max_connection_distance = max(size) * self.MAX_CONNECTION_DISTANCE_FACTOR
        self.max_connection_distance = None

    def set_rooms_distances(self, rooms_distances):
        self.rooms_distances = rooms_distances
        self.rooms = list(self.rooms_distances.keys())
        self.corridors = []

    def get_all_connected_to(self, room, connections=None):
        """Return recursively all connected rooms with given room."""
        connections = connections or set()
        connections.add(room)
        for connected in room.connected_rooms:
            if connected in connections:
                continue
            connections.update(self.get_all_connected_to(connected, connections))
        return connections

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
        if self.max_connection_distance and distance > self.max_connection_distance:
            # Room too far
            return False
        return True

    def nearest_rooms(self, room):
        """Yield (distance, other) pairs from nearest to furthest room."""
        for distance, others in sorted(self.rooms_distances[room]):
            for other in self.rng.sample(others, len(others)):
                yield distance, other

    def create_connection(self, room, other, corridors):
        self.corridors.extend(corridors)
        corridors[0].allow_door(0)
        corridors[-1].allow_door(-1)
        room.connected_rooms.add(other)
        other.connected_rooms.add(room)

    # Room to other connections

    def connect_to_nearest(self, room, include_rooms=None):
        """Try connecting given room with closest valid room, not yet connected with it."""
        connected = None
        if include_rooms is None:
            include_rooms = self.rooms
        for distance, other in self.nearest_rooms(room):
            if not self.is_connection_valid(room, other, distance, include_rooms):
                continue
            corridors = self.generate_corridors(room, other)
            if corridors:
                self.create_connection(room, other, corridors)
                connected = other
                break
        log.debug(f'Connected: {self.rooms.index(room)} -> {connected and self.rooms.index(connected)}')
        return connected

    def connect_to_unconnected(self, room):
        """Try connecting given room to nearest room with no connections."""
        unconnected_rooms = {r for r in self.rooms if not r.connected_rooms}
        other = self.connect_to_nearest(room, unconnected_rooms)
        return other

    def connect_to_connected(self, room):
        """Try connecting given room to nearest room with connections."""
        connected_rooms = {r for r in self.rooms if r.connected_rooms}
        other = self.connect_to_nearest(room, connected_rooms)
        return other

    # Rooms connecting algorithms

    def follow_path_of_unconnected(self, room=None):
        """Keep connecting not yet connected rooms to create path from starting room.

        If no room is provided randomly select one.

        """
        room = room or self.rng.choice(self.rooms)
        while room:
            other = self.connect_to_unconnected(room)
            # Use this room as new starting one
            room = other

    def randomly_connect_to_nearest(self, rooms=None, rooms_num=None):
        """In random order connect rooms to nearest room."""
        rooms = rooms or self.rooms
        rooms_num = rooms_num or len(rooms)
        for room in self.rng.sample(rooms, rooms_num):
            other = self.connect_to_nearest(room, rooms)

    def connect_without_connections(self):
        """Connect all rooms with no connections to already connected ones."""
        without_connections = [room for room in self.rooms if not room.connected_rooms]
        tries = len(without_connections)*5
        log.debug(f'Without connections: {len(without_connections)}')
        while without_connections and tries:
            room = self.rng.choice(without_connections)
            other = self.connect_to_connected(room)
            without_connections = [r for r in self.rooms if not r.connected_rooms]
            tries -= 1

    def extra_random_connections(self, connections_num):
        """Create given number of extra connections."""
        log.debug(f'Extra connections: {connections_num}')
        while connections_num:
            room = self.rng.choice(self.rooms)
            other = self.connect_to_nearest(room)
            if other:
                connections_num -= 1

    def connect_separete(self):
        """Connect separate sets of rooms."""
        connected = self.get_all_connected_to(self.rng.choice(self.rooms))
        while not len(connected) == len(self.rooms):
            unconnected = {r for r in self.rooms if not r in connected}
            other = self.connect_to_nearest(
                self.rng.choice(list(connected)),
                unconnected
            )
            connected = self.get_all_connected_to(self.rng.choice(self.rooms))
            self.max_connection_distance += 1

    def generate_connections():
        raise NotImplementedError()

    def connect_rooms(self, rooms_distances):
        self.set_rooms_distances(rooms_distances)

        self.generate_connections()
        self.connect_separete()

        return self.corridors


class RandomToNearestRoomsConnector(RoomsConnector):

    def generate_connections(self):
        self.max_connection_distance = 2

        self.randomly_connect_to_nearest()
        self.max_connection_distance += 2
        self.connect_without_connections()

        extra_connections_num = self.rng.randint(1, int(math.sqrt(len(self.rooms))))
        self.extra_random_connections(extra_connections_num)

        return self.corridors


class FollowToNearestRoomsConnector(RoomsConnector):

    """Connection algorithm similar to original Rogue.

    See: https://web.archive.org/web/20131025132021/http://kuoi.org/~kamikaze/GameDesign/art07_rogue_dungeon.php

    """

    def generate_connections(self):
        self.max_connection_distance = 2

        self.follow_path_of_unconnected()
        self.connect_without_connections()

        extra_connections_num = self.rng.randint(1, int(math.sqrt(len(self.rooms))))
        self.extra_random_connections(extra_connections_num)

        return self.corridors


class BSPRoomsConnector(RoomsConnector):

    def generate_connections(self):
        self.max_connection_distance = 2

        while not len(self.get_all_connected_to(self.rooms[0])) == len(self.rooms):
            skip_rooms = set()
            for room in self.rooms:
                if room in skip_rooms:
                    continue
                connected_to_room = self.get_all_connected_to(room)
                unconnected_to_room = {r for r in self.rooms if not r in connected_to_room}
                other = self.connect_to_nearest(
                    self.rng.choice(list(connected_to_room)),
                    unconnected_to_room
                )
                if other:
                    skip_rooms.update(self.get_all_connected_to(other))
            self.max_connection_distance += 2

        extra_connections_num = self.rng.randint(1, int(math.sqrt(len(self.rooms))))
        self.extra_random_connections(extra_connections_num)

        return self.corridors

