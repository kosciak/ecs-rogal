import collections

from .core import Position, Size, WithPositionMixin, WithSizeMixin


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

    @property
    def positions(self):
        """Return set of Positions inside this Rectangle."""
        positions = set()
        for y in range(self.y, self.y2):
            for x in range(self.x, self.x2):
                positions.add(Position(x, y))
        return positions

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


def split_vertical(rectangular, left=None, right=None):
    width = left or right
    if width < 1:
        width = int(rectangular.width * width)
    if right:
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


def split_horizontal(rectangular, top=None, bottom=None):
    height = top or bottom
    if height < 1:
        height = int(rectangular.height * height)
    if bottom:
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


def split_rect(rectangular, left=None, right=None, top=None, bottom=None):
    if left or right:
        return split_vertical(rectangular, left=left, right=right)
    if top or bottom:
        return split_horizontal(rectangular, top=top, bottom=bottom)

