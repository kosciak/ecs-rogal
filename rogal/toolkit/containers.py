import functools

from ..collections.attrdict import OrderedAttrDict

from ..geometry import Position, Size

from ..console.core import Align

from . import core


class Bin(core.Container, core.WithSize):

    """Container with only one child element."""

    def __init__(self, content, **kwargs):
        self.content = content
        super().__init__(**kwargs)

    @property
    def align(self):
        align = self.style.align
        if align is None:
            align = self.content.align
        return align

    def get_min_width(self, available):
        if self.style.width is not None:
            width = super().get_min_width(available)
        else:
            width = self.content.get_min_width(available)
        return width

    def get_min_height(self, available):
        if self.style.height is not None:
            height = super().get_min_height(available)
        else:
            height = self.content.get_min_height(available)
        return height

    def layout_content(self, manager, panel, z_order):
        _, z_order = self.content.layout(
            manager, panel, z_order+1, recalc=False,
        )
        return z_order

    def __iter__(self):
        yield self.content


class ListContainer(core.Container):

    """Mixin for containers with child elements stored in a list."""

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


class Stack(ListContainer, core.WithSize):

    """Free form container where all children are stacked on top of each other.

    Elements are rendered in FIFO order and each element use whole panel.
    Will overdraw previous ones if they overlap.

    """

    def layout_content(self, manager, panel, z_order):
        for child in self.content:
            _, z_order = child.layout(
                manager, panel, z_order+1, recalc=True,
            )
        return z_order


class NamedStack(core.Container, core.WithSize):

    """Works like Stack, but content is an ordered dict."""

    def __init__(self, content=None, **kwargs):
        self.content = OrderedAttrDict()
        if content:
            self.content.update(content)
        super().__init__(**kwargs)

    def layout_content(self, manager, panel, z_order):
        for child in self.content.values():
            _, z_order = child.layout(
                manager, panel, z_order+1, recalc=True,
            )
        return z_order

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        yield from self.content.values()


@functools.lru_cache(maxsize=None)
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


class Row(ListContainer, core.WithSize):

    """Horizontal container.

    Elements are rendererd in FIFO order from left to right.

    align=LEFT    |AA BB CC      |
    align=RIGHT   |      AA BB CC|
    align=CENTER  |   AA BB CC   |

    """

    def get_min_width(self, available):
        if self.style.width is not None:
            width = super().get_min_width(available)
        else:
            widths = [child.get_min_width(available) for child in self.content]
            if self.FULL_SIZE in widths:
                width = self.FULL_SIZE
            else:
                width = sum(widths)
        return width

    def get_min_height(self, available):
        if self.style.height is not None:
            height = super().get_min_height(available)
        else:
            widths = tuple(child.get_min_width(available) for child in self.content)
            # NOTE: min_height might depend on given width so compute it first!
            calc_widths = calc_sizes(available.width, widths)
            heights = [
                child.get_min_height(Size(calc_widths[i], available.height))
                for i, child in enumerate(self.content)
            ]
            if heights and not self.FULL_SIZE in heights:
                height = max(heights)
            else:
                height = self.FULL_SIZE
        return height

    def layout_content(self, manager, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        # TODO: ??? Might need same layouting mechanism as Column does
        widths = tuple(child.get_min_width(panel) for child in self.content)
        calc_widths = calc_sizes(panel.width, widths)
        for i, child in enumerate(self.content):
            size = Size(calc_widths[i], panel.height)
            child_panel = panel.create_panel(position, size)
            _, child_z_order = child.layout(
                manager, child_panel, z_order+1, recalc=False,
            )
            z_orders.append(child_z_order or 0)
            position += Position(calc_widths[i], 0)
        return max(z_orders)


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass


class Column(ListContainer, core.WithSize):

    """Vertical container.

    Elements are rendererd in FIFO order from top to bottom.

    """

    def get_min_width(self, available):
        if self.style.width is not None:
            width = super().get_min_width(available)
        else:
            widths = [child.get_min_width(available) for child in self.content]
            if widths and not self.FULL_SIZE in widths:
                width = max(widths)
            else:
                width = self.FULL_SIZE
        return width

    def get_min_height(self, available):
        if self.style.height is not None:
            height = super().get_min_height(available)
        else:
            heights = [child.get_min_height(available) for child in self.content]
            if self.FULL_SIZE in heights:
                height = self.FULL_SIZE
            else:
                height = sum(heights)
        return height

    def layout_content(self, manager, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        min_sizes = [child.get_min_size(panel) for child in self.content]
        heights = tuple(size.height for size in min_sizes)
        calc_heights = calc_sizes(panel.height, heights)
        for i, child in enumerate(self.content):
            width = min_sizes[i].width
            if width == self.FULL_SIZE:
                width = panel.width
            height = calc_heights[i]
            child_size = Size(width, height)
            child_panel = panel.create_panel(
                position, Size(panel.width, height),
            )
            if not child_size == child_panel.size:
                # NOTE: Not calling get_layout_panel(child_panel, child_size)
                #       As Padded would stack another paddings
                child_position = child_panel.get_position(
                    child_size, child.align,
                )
                child_panel = child_panel.create_panel(
                    child_position, child_size,
                )
            _, child_z_order = child.layout(
                manager, child_panel, z_order+1, recalc=False,
            )
            z_orders.append(child_z_order or 0)
            position += Position(0, height)
        return max(z_orders)


class Split(ListContainer, core.WithSize):

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
                _, child_z_order = child.layout(
                    manager, subpanels[i], z_order+1, recalc=False,
                )
                z_orders.append(child_z_order or 0)
            if i >= 2:
                break
        if z_orders:
            z_order = max(z_orders)
        return z_order


class WithListContainer:

    def append(self, element):
        self._container.append(element)

    def extend(self, elements):
        self._container.extend(elements)

    def remove(self, element):
        self._container.remove(element)

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        # TODO: This might / should(?) mess up Container.insert() logic relying on __iter__
        yield from self._container

