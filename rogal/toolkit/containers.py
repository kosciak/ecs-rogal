from ..geometry import Position, Size

from ..console.core import Align

from . import core


class MultiContainer(core.Container):

    """Mixin for containers with multiple child elements."""

    def __init__(self, content=None, **kwargs):
        self.content = []
        if isinstance(content, (list, tuple)):
            self.extend(content)
        elif content is not None:
            self.append(content)
        super().__init__(**kwargs)

    def append(self, element):
        self.content.append(element)

    def extend(self, elements):
        self.content.extend(elements)

    def remove(self, element):
        self.content.remove(element)

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        yield from self.content


class Bin(core.Container, core.UIElement):

    """Container with only one child element."""

    def __init__(self, content, **kwargs):
        self.content = content
        super().__init__(**kwargs)

    @property
    def align(self):
        if self.style.align is not None:
            return self.style.align
        return self.content.align

    @property
    def width(self):
        if self.style.width is not None:
            return self.style.width
        return self.content.min_width

    @property
    def height(self):
        if self.style.height is not None:
            return self.style.height
        return self.content.min_height

    def layout_content(self, manager, panel, z_order):
        _, z_order = self.content.layout(manager, panel, z_order+1)
        return z_order

    def __iter__(self):
        yield self.content


class Stack(MultiContainer, core.UIElement):

    """Free form container where all children are stacked on top of each other.

    Elements are rendered in FIFO order and each element use whole panel.
    Will overdraw previous ones if they overlap.

    """

    def layout_content(self, manager, panel, z_order):
        for child in self.content:
            _, z_order = child.layout(manager, panel, z_order+1)
        return z_order


def calc_sizes(available_size, sizes):
    if all(sizes):
        return sizes
    # Calc size for fixed size elements
    reserved = sum(size for size in sizes if size)
    left = available_size - reserved
    # Now calc default size for elements without fixed size
    dynamic_num = len([size for size in sizes if not size])
    default_size = left // dynamic_num
    # TODO: What about modulo?
    return [size or default_size for size in sizes]


class Row(MultiContainer, core.UIElement):

    """Horizontal container.

    Elements are rendererd in FIFO order from left to right.

    align=LEFT    |AA BB CC      |
    align=RIGHT   |      AA BB CC|
    align=CENTER  |   AA BB CC   |

    """

    @property
    def min_width(self):
        if self.style.width is not None:
            return self.style.width
        widths = [child.min_width for child in self.content]
        if self.FULL_SIZE in widths:
            return self.FULL_SIZE
        return sum(widths)

    @property
    def min_height(self):
        if self.style.height is not None:
            return self.style.height
        heights = [child.min_height for child in self.content]
        if self.FULL_SIZE in heights:
            return self.FULL_SIZE
        heights.append(self.FULL_SIZE)
        return max(heights)

    def layout_content(self, manager, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        widths = [child.min_width for child in self.content]
        calc_widths = calc_sizes(panel.width, widths)
        for i, child in enumerate(self.content):
            # size = Size(calc_widths[i], child.height or panel.height)
            size = Size(calc_widths[i], panel.height)
            subpanel = panel.create_panel(position, size)
            _, child_z_order = child.layout(manager, subpanel, z_order+1)
            z_orders.append(child_z_order or 0)
            position += Position(calc_widths[i], 0)
        return max(z_orders)


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass


class List(MultiContainer, core.UIElement):

    """Vertical container.

    Elements are rendererd in FIFO order from top to bottom.

    """

    @property
    def min_width(self):
        if self.style.width is not None:
            return self.style.width
        widths = [child.min_width for child in self.content]
        if self.FULL_SIZE in widths:
            return self.FULL_SIZE
        widths.append(self.FULL_SIZE)
        return max(widths)

    @property
    def min_height(self):
        if self.style.height is not None:
            return self.style.height
        heights = [child.min_height for child in self.content]
        if self.FULL_SIZE in heights:
            return self.FULL_SIZE
        return sum(heights)

    def layout_content(self, manager, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        heights = [child.min_height for child in self.content]
        calc_heights = calc_sizes(panel.height, heights)
        for i, child in enumerate(self.content):
            # NOTE: Use whole panel.width instead of child.width 
            #       for containers (e.g. Row) to work correctly
            size = Size(panel.width, calc_heights[i])
            subpanel = panel.create_panel(position, size)
            _, child_z_order = child.layout(manager, subpanel, z_order+1)
            z_orders.append(child_z_order or 0)
            position += Position(0, calc_heights[i])
        return max(z_orders)


class Split(MultiContainer, core.UIElement):

    """Container that renders elements on each side of splitted panel."""

    def __init__(self, content=None, *,
                 left=None, right=None, top=None, bottom=None,
                ):
        super().__init__(content=content)
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def layout_content(self, manager, panel, z_order):
        z_orders = []
        subpanels = panel.split(self.left, self.right, self.top, self.bottom)
        for i, child in enumerate(self.content):
            if child:
                _, child_z_order = child.layout(manager, subpanels[i], z_order+1)
                z_orders.append(child_z_order or 0)
            if i >= 2:
                break
        if z_orders:
            z_order = max(z_orders)
        return z_order


class WithContainer:

    def append(self, element):
        self._container.append(element)

    def extend(self, elements):
        self._container.extend(elements)

    def remove(self, element):
        self._container.remove(element)

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        yield from self._container

