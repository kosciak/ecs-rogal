import collections
import math


class Size(collections.namedtuple(
    'Size', [
        'width', 
        'height',
    ])):

    __slots__ = ()

    @property
    def area(self):
        """Calculate the area of a rectangle of this size."""
        return self.width * self.height

    def __repr__(self):
        return f'<Size width={self.width}, height={self.height}>'


class Direction(collections.namedtuple(
    'Position', [
        'dx', 
        'dy',
    ])):

    def __repr__(self):
        return f'<Direction dx={self.dx}, dy={self.dy}>'


class Position(collections.namedtuple(
    'Position', [
        'x', 
        'y',
    ])):

    def distance(self, other):
        if not other:
            return None
        x = self.x - other.x
        y = self.x - other.y
        return math.hypot(x, y)

    def move(self, direction):
        if not direction:
            return self
        return Position(self.x+direction.dx, self.y+direction.dy)

    def __repr__(self):
        return f'<Position x={self.x}, y={self.y}>'


class Rectangle:

    __slots__ = ('position', 'size')

    def __init__(self, position, size):
        self.position = position
        self.size = size

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
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

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
        return Position(int(self.width/2), int(self.height/2))

    def __iter__(self):
        """Iterate Positions inside this Rectangle."""
        for y in range(self.y, self.y2+1):
            for x in range(self.x, self.x2+1):
                yield Position(x, y)

    @property
    def positions(self):
        """Return set of Positions inside this Rectangle."""
        return set(iter(self))

    def is_inside(self, position):
        """Return True if given Position is inside this Rectangle."""
        if not position:
            return False
        return (self.x <= x <= self.x2 and
                self.y <= y <= self.y2)

    def __contains__(self, position):
        return self.is_inside(position)

    def intersection(self, other):
        """Return the intersection with another ``Rectangle``.

        Returns ``None`` if the geometries don't intersect. 

        """
        # TODO: Test it!
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

    def __eq__(self, other):
        return self.position == other.position and self.size == other.size

    def __repr__(self):
        return '<Rectangle x=%s, y=%s, width=%s, height=%s, x2=%s, y2=%s>' % \
               (self.x, self.y, self.width, self.height, self.x2, self.y2)

