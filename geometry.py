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


class Geometry:

    __slots__ = ('position', 'size')

    def __init__(self, position, size):
        self.position = position
        self.size = size

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @property
    def x2(self):
        """X coordinate of bottom right corner."""
        return self.position.x + self.size.width

    @property
    def y2(self):
        """Y coordinate of bottom right corner."""
        return self.position.y + self.size.height

    @property
    def center(self):
        """Return center Position."""
        return Position(int(self.size.width/2), int(self.size.height/2))

    @property
    def area(self):
        return self.size.area

    def is_inside(self, position):
        """Return True if given Coord is inside extent."""
        if not position:
            return False
        return (self.position.x <= position.x <= self.x2 and
                self.position.y <= position.y <= self.y2)

    def __contains__(self, coord):
        return self.is_inside(coord)

    def intersection(self, other):
        """Return the intersection with another ``Geometry``.

        Returns ``None`` if the geometries don't intersect. 

        """
        if not other:
            return None
        x = max(self.position.x, other.position.x)
        y = max(self.position.y, other.position.y)
        width = min(self.x2, other.x2) - x
        height = min(self.y2, other.y2) - y
        if width > 0 and height > 0:
            return Geometry(Position(x, y), Size(width, height))
        else:
            return None

    def __and__(self, other):
        return self.intersection(other)

    def __eq__(self, other):
        return self.position == other.position and self.size == other.size

    def __repr__(self):
        return '<Geometry x=%s, y=%s, width=%s, height=%s, x2=%s, y2=%s>' % \
               (self.position.x, self.position.y, 
                self.size.width, self.size.height, 
                self.x2, self.y2)

