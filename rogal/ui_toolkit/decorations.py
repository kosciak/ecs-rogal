from ..geometry import Position, Size

from . import core
from . import renderers


"""UIElements that wrap other UI elements and change their look."""


class Padded(core.UIElement):

    def __init__(self, content, padding):
        super().__init__(align=content.align)
        self.content = content
        self.default_z_order = self.content.default_z_order
        self.padding = padding

    @property
    def width(self):
        width = self.content.width
        if width:
            return width + self.padding.left + self.padding.right
        return 0

    @property
    def height(self):
        height = self.content.height
        if height:
            return height + self.padding.top + self.padding.bottom
        return 0

    def get_inner_panel(self, panel):
        position = Position(self.padding.left, self.padding.top)
        size = Size(
            panel.width - self.padding.left - self.padding.right,
            panel.height - self.padding.top - self.padding.bottom,
        )
        return panel.create_panel(position, size)

    def layout_content(self, manager, parent, panel, z_order):
        element = manager.create_child(parent)
        panel = self.get_inner_panel(panel)
        return self.content.layout(manager, element, panel, z_order+1)


class Framed(core.UIElement):

    """Frame with element rendered inside."""

    def __init__(self, content, frame, *, align=None):
        super().__init__(align=align)
        self.content = content
        self.frame = frame

    @property
    def width(self):
        width = self.content.width
        if width:
            return width + self.frame.extents.width
        return 0

    @property
    def height(self):
        height = self.content.height
        if height:
            return height + self.frame.extents.height
        return 0

    def layout_content(self, manager, parent, panel, z_order):
        element = manager.create_child(parent)
        self.frame.layout(manager, element, panel, z_order+1)
        element = manager.create_child(parent)
        panel = self.frame.get_inner_panel(panel)
        return self.content.layout(manager, element, panel, z_order+2)


class Cleared(core.UIElement):

    def __init__(self, content, *, colors=None):
        super().__init__(
            width=content.width,
            height=content.height,
            align=content.align,
        )
        self.content = content
        self.renderer = renderers.ClearPanel(
            colors=colors,
        )

    @property
    def colors(self):
        return self.renderer.colors

    @colors.setter
    def colors(self, colors):
        self.renderer.colors = colors

    def layout_content(self, manager, parent, panel, z_order):
        element = manager.create_child(parent)
        return self.content.layout(manager, element, panel, z_order+1)

