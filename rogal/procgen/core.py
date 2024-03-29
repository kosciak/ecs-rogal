import collections
import logging

from ..geometry import Position, Size
from ..geometry.rectangle import Rectangular, Rectangle
from ..rng import RNG


log = logging.getLogger(__name__)


class Generator:

    """Abstract Generator class. Use existing RNG or init new using given seed."""

    def __init__(self, rng=None, seed=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rng = rng or self.init_rng(seed)

    def init_rng(self, seed=None):
        """Init RNG with given seed, or generate new seed."""
        return RNG(seed, dump=self.__class__.__name__)

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


class OffsetedRectangle(Rectangular):

    __slots__ = ('position', 'size', 'inner', )

    OFFSET = Position.ZERO

    def __init__(self, position, size):
        self.position = position-self.OFFSET
        self.size = Size(size.width+self.OFFSET.x, size.height+self.OFFSET.y)
        self.inner = Rectangle(position, size)

    @property
    def center(self):
        return self.inner.center


class Digable(OffsetedRectangle):

    def dig_floor(self, terrain, floor):
        terrain[self.inner.x:self.inner.x2, self.inner.y:self.inner.y2] = floor

