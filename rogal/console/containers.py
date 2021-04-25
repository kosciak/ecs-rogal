from ..geometry import Position, Size

from .core import Padding
from . import toolkit


class Stack(toolkit.Container):

    """Free form container where all children are stacked on top of each other."""

    def layout_content(self, manager, parent, panel, z_order):
        for child in self.children:
            widget = manager.create_child(parent)
            z_order = child.layout(manager, widget, panel, z_order+1)
        return z_order


class Row(toolkit.Container, toolkit.Widget):

    """Horizontal container.

    Widgets are rendererd in FIFO order from left to right.

    align=LEFT    |AA BB CC      |
    align=RIGHT   |      AA BB CC|
    align=CENTER  |   AA BB CC   |

    """

    def __init__(self, content=None, *, align, padding=Padding.ZERO):
        super().__init__(content=content, align=align, padding=padding)

    @property
    def size(self):
        if not self.children:
            return None
        return Size(
            sum([widget.padded_width for widget in self.children]),
            max([widget.padded_height for widget in self.children])
        )

    def layout_content(self, manager, parent, panel, z_order):
        children_z_orders = []
        position = panel.get_position(self.size, self.align)
        for child in self.children:
            widget = manager.create_child(parent)
            subpanel = panel.create_panel(position, child.padded_size)
            child_z_order = child.layout(manager, widget, subpanel, z_order+1)
            children_z_orders.append(child_z_order or 0)
            position += Position(child.padded_width, 0)
        return children_z_orders and max(children_z_orders) or z_order


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass


class List(toolkit.Container, toolkit.Widget):

    """Vertical container.

    Widgets are rendererd in FIFO order from top to bottom.

    """

    def __init__(self, content=None, *, align, padding=Padding.ZERO):
        super().__init__(content=content, align=align, padding=padding)

    @property
    def size(self):
        if not self.children:
            return None
        return Size(
            max([widget.padded_width for widget in self.children]),
            sum([widget.padded_height for widget in self.children])
        )

    def layout_content(self, manager, parent, panel, z_order):
        children_z_orders = []
        position = panel.get_position(self.size, self.align)
        for child in self.children:
            widget = manager.create_child(parent)
            subpanel = panel.create_panel(position, child.padded_size)
            child_z_order = child.layout(manager, widget, subpanel, z_order+1)
            children_z_orders.append(child_z_order or 0)
            position += Position(0, child.padded_height)
        return children_z_orders and max(children_z_orders) or z_order



class Split(toolkit.Container):

    """Container that renders widgets on each side of splitted panel."""

    def __init__(self, content=None, *, left=None, right=None, top=None, bottom=None):
        super().__init__(content=content)
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def layout_content(self, manager, parent, panel, z_order):
        children_z_orders = []
        subpanels = panel.split(self.left, self.right, self.top, self.bottom)
        for i, child in enumerate(self.children):
            if child:
                widget = manager.create_child(parent)
                child_z_order = child.layout(manager, widget, subpanels[i], z_order+1)
                children_z_orders.append(child_z_order or 0)
            if i >= 2:
                break
        return children_z_orders and max(children_z_orders) or z_order

