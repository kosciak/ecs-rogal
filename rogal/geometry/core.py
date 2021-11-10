import collections
from enum import Enum

from .distance import euclidean_distance


class Vector(collections.namedtuple(
    'Vector', [
        'dx',
        'dy',
    ])):

    """Vector on 2d plane."""

    __slots__ = ()

    def __bool__(self):
        # NOTE: Vector(0, 0) is considered False
        return bool(self.dx or self.dy)

    def __repr__(self):
        return f'<Vector dx={self.dx}, dy={self.dy}>'

Vector.ZERO = Vector(0, 0)


# TODO: Move to movement related something?
class Direction(Vector, Enum):

    """Direction on 2D plane."""

    N = (0, -1)
    NE = (1, -1)
    E = (1, 0)
    SE = (1, 1)
    S = (0, 1)
    SW = (-1, 1)
    W = (-1, 0)
    NW = (-1, -1)

    @property
    def is_diagonal(self):
        return all(self.value)

    @property
    def is_cardinal(self):
        return not self.is_diagonal

    def __repr__(self):
        return f'<Direction dx={self.dx}, dy={self.dy}>'


class Position(collections.namedtuple(
    'Position', [
        'x',
        'y',
    ])):

    """Position on 2D plane."""

    __slots__ = ()

    def __new__(cls, x, y):
        return super().__new__(cls, int(x), int(y))

    def offset(self, other):
        """Return position of self in relation to other."""
        return self - other

    def distance(self, other, distance_fn=euclidean_distance):
        """Return distance between two Positions."""
        if not other:
            return None
        return distance_fn(self, other)

    def moved_from(self, vector):
        """Return Position from where it was moved by given Vector."""
        if not vector:
            return self
        return Position(self.x-vector.dx, self.y-vector.dy)

    def move(self, vector):
        """Return Position after moving by given Vector."""
        if not vector:
            return self
        return Position(self.x+vector.dx, self.y+vector.dy)

    def __add__(self, other):
        if not other:
            return None
        return Position(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        if not other:
            return None
        return Position(self.x-other.x, self.y-other.y)

    def __repr__(self):
        return f'<Position x={self.x}, y={self.y}>'

Position.ZERO = Position(0, 0)


class WithPositionMixin:

    """Mixin for easy acces to Position related methods and properties."""

    __slots__ = ()

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y


class Size(collections.namedtuple(
    'Size', [
        'width',
        'height',
    ])):

    """Size on 2D plane."""

    __slots__ = ()

    def __new__(cls, width, height):
        return super().__new__(cls, int(width), int(height))

    @property
    def area(self):
        """Calculate the area of a rectangle of this size."""
        return self.width * self.height

    def __mul__(self, factor):
        """Resize by factor value."""
        return Size(self.width*factor, self.height*factor)

    def __repr__(self):
        return f'<Size width={self.width}, height={self.height}>'


class WithSizeMixin:

    """Mixin for easy acces to Size related methods and properties."""

    __slots__ = ()

    @property
    def width(self):
        return self.size.width

    @property
    def height(self):
        return self.size.height

    @property
    def area(self):
        return self.size.area

    @property
    def center(self):
        """Return center Position relative to self."""
        return Position(self.width/2, self.height/2)

