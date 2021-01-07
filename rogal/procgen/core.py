import logging
import random
import uuid

from ..geometry import Position, Size, Rectangle


log = logging.getLogger(__name__)


SEED = None
#SEED = uuid.UUID( '137ad920-fd42-470a-a99c-6ed52b7c05b5' )


class Generator:

    """Abstract Generator class. Use existing RNG or init new using given seed."""

    def __init__(self, rng=None, seed=None):
        self.rng = rng or self.init_rng(seed)

    def init_rng(self, seed=None):
        """Init RNG with given seed, or generate new seed."""
        if seed is None:
            seed = uuid.uuid4()
        log.debug(f'Generator seed: {seed}')
        rng = random.Random(seed)
        return rng


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


class Digable(OffsetedRectangle):

    def dig_floor(self, level, floor):
        level.terrain[self.inner.x:self.inner.x2, self.inner.y:self.inner.y2] = floor.id


class Room(Digable):

    """Rectangular room.

    Left and top border are considered walls, so rooms can share walls with each other when adjecent.

    Room with Size(5, 3) has inner floor area of Size(4, 2) with offset (1, 1)

    #####
    #....
    #....

    """

    INNER_OFFSET = Position(1, 1)

    def __init__(self, position, size):
        super().__init__(position, size)
        self.connected_rooms = set()

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

    INNER_OFFSET = Position(1, 0)

    is_horizontal = False

    def __init__(self, position, length):
        self.length = length
        super().__init__(position, Size(1, self.length))

    def get_position(self, length):
        if length < 0:
            length += self.length
        return Position(self.inner.x, self.y+length)


class HorizontalCorridor(Corridor):

    """Horizontal corridor.

    #####
    .....

    """

    INNER_OFFSET = Position(0, 1)

    is_horizontal = True

    def __init__(self, position, length):
        self.length = length
        super().__init__(position, Size(self.length, 1))

    def get_position(self, length):
        if length < 0:
            length += self.length
        return Position(self.x+length, self.inner.y)

