from ..geometry import Position, Size

from ..console.core import Align

from . import core


class Bin(core.UIElement):

    """UIElement containing single content element."""

    def __init__(self, content, *, align=None, width=None, height=None):
        super().__init__(
            align=align,
            width=width,
            height=height,
        )
        self.content = content

    @core.UIElement.align.getter
    def align(self):
        if self.style.align is not None:
            return self.style.align
        return self.content.align

    @core.UIElement.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        return self.content.min_width

    @core.UIElement.height.getter
    def height(self):
        if self.style.height is not None:
            return self.style.height
        return self.content.min_height

    def layout_content(self, manager, parent, panel, z_order):
        element = manager.create_child(parent)
        return self.content.layout(manager, element, panel, z_order+1)

    def __iter__(self):
        yield self.content


class Stack(core.Container, core.UIElement):

    """Free form container where all children are stacked on top of each other.

    UIElements are rendered in FIFO order and each element use whole panel.
    Will overdraw previous ones if they overlap.

    """

    def layout_content(self, manager, parent, panel, z_order):
        for child in self.content:
            element = manager.create_child(parent)
            z_order = child.layout(manager, element, panel, z_order+1)
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


class Row(core.Container, core.UIElement):

    """Horizontal container.

    UIElements are rendererd in FIFO order from left to right.

    align=LEFT    |AA BB CC      |
    align=RIGHT   |      AA BB CC|
    align=CENTER  |   AA BB CC   |

    """

    def __init__(self, content=None, *, align=None, width=None, height=None):
        if align is None:
            align = Align.LEFT
        super().__init__(
            content=content,
            align=align,
            width=width,
            height=height,
        )

    @core.UIElement.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        widths = [child.min_width for child in self.content]
        if self.FULL_SIZE in widths:
            return self.FULL_SIZE
        return sum(widths)

    @core.UIElement.height.getter
    def height(self):
        if self.style.height is not None:
            return self.style.height
        heights = [child.min_height for child in self.content]
        if self.FULL_SIZE in heights:
            return self.FULL_SIZE
        heights.append(self.FULL_SIZE)
        return max(heights)

    def layout_content(self, manager, parent, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        widths = [child.min_width for child in self.content]
        calc_widths = calc_sizes(panel.width, widths)
        for i, child in enumerate(self.content):
            element = manager.create_child(parent)
            # size = Size(calc_widths[i], child.height or panel.height)
            size = Size(calc_widths[i], panel.height)
            subpanel = panel.create_panel(position, size)
            child_z_order = child.layout(manager, element, subpanel, z_order+1)
            z_orders.append(child_z_order or 0)
            position += Position(calc_widths[i], 0)
        return max(z_orders)


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass


class List(core.Container, core.UIElement):

    """Vertical container.

    UIElements are rendererd in FIFO order from top to bottom.

    """

    def __init__(self, content=None, *, align=None, width=None, height=None):
        if align is None:
            align = Align.TOP
        super().__init__(
            content=content,
            align=align,
            width=width,
            height=height,
        )

    @core.UIElement.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        widths = [child.min_width for child in self.content]
        if self.FULL_SIZE in widths:
            return self.FULL_SIZE
        widths.append(self.FULL_SIZE)
        return max(widths)

    @core.UIElement.height.getter
    def height(self):
        if self.style.height is not None:
            return self.style.height
        heights = [child.min_height for child in self.content]
        if self.FULL_SIZE in heights:
            return self.FULL_SIZE
        return sum(heights)

    def layout_content(self, manager, parent, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        heights = [child.min_height for child in self.content]
        calc_heights = calc_sizes(panel.height, heights)
        for i, child in enumerate(self.content):
            element = manager.create_child(parent)
            # NOTE: Use whole panel.width instead of child.width 
            #       for containers (e.g. Row) to work correctly
            size = Size(panel.width, calc_heights[i])
            subpanel = panel.create_panel(position, size)
            child_z_order = child.layout(manager, element, subpanel, z_order+1)
            z_orders.append(child_z_order or 0)
            position += Position(0, calc_heights[i])
        return max(z_orders)


class Split(core.Container, core.UIElement):

    """Container that renders elements on each side of splitted panel."""

    def __init__(self, content=None, *, left=None, right=None, top=None, bottom=None):
        super().__init__(content=content)
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def layout_content(self, manager, parent, panel, z_order):
        z_orders = []
        subpanels = panel.split(self.left, self.right, self.top, self.bottom)
        for i, child in enumerate(self.content):
            if child:
                element = manager.create_child(parent)
                child_z_order = child.layout(manager, element, subpanels[i], z_order+1)
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

