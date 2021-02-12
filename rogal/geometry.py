import collections
from enum import Enum
import math


def euclidean_distance(position, other):
    """Return Euclidean distance between points."""
    delta_x = position.x - other.x
    delta_y = position.y - other.y
    return math.hypot(delta_x, delta_y)


def chebyshev_distance(position, other):
    """Return Chebyshev distance between points.

    AKA chessboard distance, both ordinal and diagonal movements has the same cost.

    """
    return max(abs(position.x-other.x), abs(position.y-other.y))


def manhattan_distance(position, other):
    """Return Manhattan distance between points.

    AKA taxicab distance - sum of absolute differences. Diagonal movement has twice the cost.

    """
    return abs(position.x-other.x) + abs(position.y-other.y)


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

    def move(self, vector):
        """Return Position after moving in given Direction."""
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


class Rectangular(WithPositionMixin, WithSizeMixin):

    """Rectangle on 2D plane with Size, and Position on top-left corner."""

    __slots__ = ()

    @property
    def x2(self):
        """X coordinate of bottom right corner."""
        return self.x + self.width

    @property
    def y2(self):
        """Y coordinate of bottom right corner."""
        return self.y + self.height

    @property
    def center(self):
        """Return center Position."""
        return Position(self.x+self.width//2, self.y+self.height//2)

    def __iter__(self):
        """Iterate Positions inside this Rectangle."""
        for y in range(self.y, self.y2):
            for x in range(self.x, self.x2):
                yield Position(x, y)

    @property
    def positions(self):
        """Return set of Positions inside this Rectangle."""
        return set(iter(self))

    def is_inside(self, position):
        """Return True if given Position is inside this Rectangle."""
        if not position:
            return False
        return (self.x <= position.x < self.x2 and
                self.y <= position.y < self.y2)

    def __contains__(self, position):
        return self.is_inside(position)

    def intersection(self, other):
        """Return Rectangle that is an intersection with other Rectangle.

        Returns None if the geometries don't intersect. 

        """
        if not other:
            return None
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        width = min(self.x2, other.x2) - x
        height = min(self.y2, other.y2) - y
        if width > 0 and height > 0:
            return Rectangle(Position(x, y), Size(width, height))
        else:
            return None

    def __and__(self, other):
        return self.intersection(other)

    def __repr__(self):
        return f'<{self.__class__.__name__} x={self.x}, y={self.y}, width={self.width}, height={self.height}, x2={self.x2}, y2={self.y2}>'


class Rectangle(Rectangular, collections.namedtuple(
    'Rectangle', [
        'position',
        'size',
    ])):

    """Immutable rectangle."""

    __slots__ = ()


def split_vertical(rectangular, right=None, left=None):
    width = left or right
    if width < 1:
        width = int(rectangular.width * width)
    if left:
        width = rectangular.width - width
    left = Rectangle(
        rectangular.position,
        Size(width, rectangular.height)
    )
    right = Rectangle(
        Position(left.x2, rectangular.y),
        Size(rectangular.width-left.width, rectangular.height)
    )
    return left, right


def split_horizontal(rectangular, bottom=None, top=None):
    height = top or bottom
    if height < 1:
        height = int(rectangular.height * height)
    if top:
        height = rectangular.height - height
    top = Rectangle(
        rectangular.position,
        Size(rectangular.width, height)
    )
    bottom = Rectangle(
        Position(rectangular.x, top.y2),
        Size(rectangular.width, rectangular.height-top.height)
    )
    return top, bottom


def split(rectangular, left=None, right=None, top=None, bottom=None):
    if left or right:
        return split_vertical(rectangular, left=left, right=right)
    if top or bottom:
        return split_horizontal(rectangular, top=top, bottom=bottom)

