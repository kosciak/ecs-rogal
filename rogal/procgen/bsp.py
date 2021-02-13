import logging

from ..geometry import Rectangular, Position, Size, split_rect
from ..tree import BinaryTree

from .core import Generator


log = logging.getLogger(__name__)


class BSPTree(Rectangular, BinaryTree):

    """Binary Space Partition Tress."""

    __slots__ = ('position', 'size', )

    def __init__(self, position, size):
        super().__init__()
        self.position = position
        self.size = size

    def split(self, width=None, height=None):
        left, right = split_rect(self, left=width, top=height)
        self.left = BSPTree(*left)
        self.right = BSPTree(*right)
        return self.left, self.right


class BSPGenerator(Generator):

    MIN_SIZE = 5    # Minimal width/height
    MIN_SIZES_RATIO = .45

    def __init__(
        self, rng,
        position, size,
        min_size=MIN_SIZE,
        min_sizes_ratio=MIN_SIZES_RATIO,
    ):
        super().__init__(rng=rng)

        self.min_size = min_size
        self.min_sizes_ratio = min_sizes_ratio
        self.bsp_tree = BSPTree(position, size)

    def is_split_valid(self, left, right):
        left_sizes_ratio = min(left.size) / max(left.size)
        if left_sizes_ratio < self.min_sizes_ratio:
            return False
        right_sizes_ratio = min(right.size) / max(right.size)
        if right_sizes_ratio < self.min_sizes_ratio:
            return False
        return True

    def split(self, bsp_node, tries=50):
        if tries <= 0:
            return None, None

        width = None
        if bsp_node.width // 2 >= self.min_size:
            width = self.rng.randint(self.min_size, bsp_node.width-self.min_size)

        height = None
        if bsp_node.height // 2 >= self.min_size:
            height = self.rng.randint(self.min_size, bsp_node.height-self.min_size)

        if width is None and height is None:
            # There is no valid split possible - child nodes would be too small
            return None, None

        if width is None or height is None:
            # Only vertical OR horizontal split possible
            left, right = bsp_node.split(width=width, height=height)
        else:
            # Both splits possible, choose one randomly
            if self.rng.randbool():
                left, right = bsp_node.split(width=width)
            else:
                left, right = bsp_node.split(height=height)

        # Check if valid children were generated, if not clear results and try again
        if not self.is_split_valid(left, right):
            bsp_node.clear() # Clear children as they are not valid!
            left, right = self.split(bsp_node, tries-1)

        return left, right

    def generate(self, depth):
        self.bsp_tree.clear()

        to_split = [self.bsp_tree, ]
        splitted = []
        while depth:
            for node in to_split:
                left, right = self.split(node)
                if left:
                    splitted.append(left)
                if right:
                    splitted.append(right)

            depth -= 1
            to_split = splitted
            splitted = []

        return self.bsp_tree

