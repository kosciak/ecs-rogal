from ..geometry import Position, Size

from . import core


"""UIElements that wrap other UI elements and change their look."""


class ContentProxy:

    def __getattr__(self, name):
        return getattr(self.content, name)


class Padded(core.UIElement):

    def __init__(self, content, padding, **kwargs):
        super().__init__(align=content.align, **kwargs)
        self.content = content
        self.default_z_order = self.content.default_z_order
        self.padding = padding

    @property
    def width(self):
        width = self.content.width
        return width and (width + self.padding.left + self.padding.right) or 0

    @property
    def height(self):
        height = self.content.height
        return height and (height + self.padding.top + self.padding.bottom) or 0

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
        return width and (width + self.frame.extents.width) or 0

    @property
    def height(self):
        height = self.content.height
        return height and (height + self.frame.extents.height) or 0

    def layout_content(self, manager, parent, panel, z_order):
        element = manager.create_child(parent)
        self.frame.layout(manager, element, panel, z_order+1)
        element = manager.create_child(parent)
        panel = self.frame.get_inner_panel(panel)
        return self.content.layout(manager, element, panel, z_order+2)

