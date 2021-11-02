from ..geometry import Position, Size

from . import toolkit


class Stack(toolkit.Container, toolkit.UIElement):

    """Free form container where all children are stacked on top of each other.

    UIElements are rendered in FIFO order and each element use whole panel.
    Will overdraw previous ones if they overlap.

    """

    def layout_content(self, manager, parent, panel, z_order):
        for child in self.children:
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


class Row(toolkit.Container, toolkit.UIElement):

    """Horizontal container.

    UIElements are rendererd in FIFO order from left to right.

    align=LEFT    |AA BB CC      |
    align=RIGHT   |      AA BB CC|
    align=CENTER  |   AA BB CC   |

    """

    def __init__(self, content=None, *, align):
        super().__init__(content=content, align=align)

    @property
    def width(self):
        if self._width:
            return self._width
        widths = [child.width for child in self.children]
        if 0 in widths:
            return 0
        return sum(widths)

    @property
    def height(self):
        if self._height:
            return self._height
        heights = [child.height for child in self.children]
        if 0 in heights:
            return 0
        heights.append(0)
        return max(heights)

    def layout_content(self, manager, parent, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        widths = [child.width for child in self.children]
        calc_widths = calc_sizes(panel.width, widths)
        for i, child in enumerate(self.children):
            element = manager.create_child(parent)
            size = Size(calc_widths[i], child.height or panel.height)
            subpanel = panel.create_panel(position, size)
            child_z_order = child.layout(manager, element, subpanel, z_order+1)
            z_orders.append(child_z_order or 0)
            position += Position(calc_widths[i], 0)
        return max(z_orders)


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass


class List(toolkit.Container, toolkit.UIElement):

    """Vertical container.

    UIElements are rendererd in FIFO order from top to bottom.

    """

    def __init__(self, content=None, *, align):
        super().__init__(content=content, align=align)

    @property
    def width(self):
        if self._width:
            return self._width
        widths = [child.width for child in self.children]
        if 0 in widths:
            return 0
        widths.append(0)
        return max(widths)

    @property
    def height(self):
        if self._height:
            return self._height
        heights = [child.height for child in self.children]
        if 0 in heights:
            return 0
        return sum(heights)

    def layout_content(self, manager, parent, panel, z_order):
        z_orders = [z_order, ]
        position = Position.ZERO
        heights = [child.height for child in self.children]
        calc_heights = calc_sizes(panel.height, heights)
        for i, child in enumerate(self.children):
            element = manager.create_child(parent)
            size = Size(child.width or panel.width, calc_heights[i])
            subpanel = panel.create_panel(position, size)
            child_z_order = child.layout(manager, element, subpanel, z_order+1)
            z_orders.append(child_z_order or 0)
            position += Position(0, calc_heights[i])
        return max(z_orders)


class Split(toolkit.Container, toolkit.UIElement):

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
        for i, child in enumerate(self.children):
            if child:
                element = manager.create_child(parent)
                child_z_order = child.layout(manager, element, subpanels[i], z_order+1)
                z_orders.append(child_z_order or 0)
            if i >= 2:
                break
        return z_orders and max(z_orders) or z_order

