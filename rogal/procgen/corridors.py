import collections
import logging

from ..geometry import Position, Size
from ..rng import RandomTable

from .core import Generator, Digable


log = logging.getLogger(__name__)


class Corridor(Digable):

    def __init__(self, position, size):
        super().__init__(position, size)
        self.allowed_doors = set()

    def allow_door(self, length):
        self.allowed_doors.add(self.get_position(length))


class VerticalCorridor(Corridor):

    """Vertical corridor.

    #.
    #.
    #.

    """

    OFFSET = Position(1, 1)

    is_horizontal = False

    def __init__(self, position, length, width=1):
        self.length = length
        super().__init__(position, Size(width, self.length))

    def get_position(self, length):
        if length < 0:
            length += self.length
        return Position(self.inner.x, self.inner.y+length)


class HorizontalCorridor(Corridor):

    """Horizontal corridor.

    #####
    .....

    """

    OFFSET = Position(1, 1)

    is_horizontal = True

    def __init__(self, position, length, width=1):
        self.length = length
        super().__init__(position, Size(self.length, width))

    def get_position(self, length):
        if length < 0:
            length += self.length
        return Position(self.inner.x+length, self.inner.y)


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
        for generator_fn in self.rng.shuffled(generator_fns):
            yield from generator_fn(room, other)


class StraightCorridorGenerator(CorridorGenerator):

    """Generate straight corridor. Works only if two rooms overlaps on a plane."""

    def generate_vertical(self, room, other):
        """Yield all possible vertical corridors connecting to other room."""
        length = room.vertical_spacing(other)
        y = min(room.y2, other.y2)
        overlaps = room.horizontal_overlap(other)
        for x in self.rng.shuffled(overlaps):
            corridor = VerticalCorridor(Position(x, y), length)
            yield (corridor, )

    def generate_horizontal(self, room, other):
        """Yield all possible horizontal corridors connecting to other room."""
        length = room.horizontal_spacing(other)
        x = min(room.x2, other.x2)
        overlaps = room.vertical_overlap(other)
        for y in self.rng.shuffled(overlaps):
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


class MixedCorridorGenerator(CorridorGenerator):

    def __init__(self, corridor_generators, rng=None, seed=None, *args, **kwargs):
        super().__init__(rng=rng, seed=seed, *args, **kwargs)

        self.corridor_generators = RandomTable(self.rng, *corridor_generators)

    def generate_vertical(self, room, other):
        generator = self.corridor_generators.choice()
        return generator.generate_vertical(room, other)

    def generate_horizontal(self, room, other):
        generator = self.corridor_generators.choice()
        return generator.generate_horizontal(room, other)

