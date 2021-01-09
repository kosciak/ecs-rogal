import collections
import logging
import random
import uuid

from ..geometry import Rectangular, Position, Size, Rectangle


log = logging.getLogger(__name__)


SEED = None
#SEED = uuid.UUID( '137ad920-fd42-470a-a99c-6ed52b7c05b5' )


class Generator:

    """Abstract Generator class. Use existing RNG or init new using given seed."""

    def __init__(self, rng=None, seed=None, *args, **kwargs):
        self.rng = rng or self.init_rng(seed)

    def init_rng(self, seed=None):
        """Init RNG with given seed, or generate new seed."""
        if seed is None:
            seed = uuid.uuid4()
        log.debug(f'Generator seed: {seed}')
        rng = random.Random(seed)
        return rng


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

    def dig_floor(self, level, floor):
        level.terrain[self.inner.x:self.inner.x2, self.inner.y:self.inner.y2] = floor.id

