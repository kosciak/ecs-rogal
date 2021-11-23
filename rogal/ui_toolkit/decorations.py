from ..geometry import Position, Size

from . import core
from . import containers
from . import renderers


"""UIElements that wrap other UI elements and change their look."""


class Padded(containers.Bin):

    def __init__(self, content, padding, *, align=None):
        super().__init__(
            content=content,
            align=align,
        )
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


class WithPaddedContent:

    def __init__(self, content, padding, align=None, *args, **kwargs):
        self._padded = Padded(
            content=content,
            padding=padding,
            align=align,
        )
        super().__init__(
            content=self._padded,
            *args, **kwargs,
        )

    @property
    def padding(self):
        return self._padded.padding

    @padding.setter
    def padding(self, padding):
        self._padded.frame = padding


class Framed(containers.Bin):

    """Frame with element rendered inside."""

    def __init__(self, content, frame, *, align=None):
        super().__init__(
            content=content,
            align=align,
        )
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


class WithFramedContent:

    def __init__(self, content, frame, align=None, *args, **kwargs):
        self._framed = Framed(
            content=content,
            frame=frame,
            align=align,
        )
        super().__init__(
            content=self._framed,
            *args, **kwargs,
        )

    @property
    def frame(self):
        return self._framed.frame

    @frame.setter
    def frame(self, frame):
        self._framed.frame = frame


class Cleared(containers.Bin):

    def __init__(self, content, *, colors=None):
        super().__init__(
            content=content,
        )
        self.renderer = renderers.ClearPanel(
            colors=colors,
        )

    @property
    def colors(self):
        return self.renderer.colors

    @colors.setter
    def colors(self, colors):
        self.renderer.colors = colors


class WithClearedContent:

    def __init__(self, content, colors, *args, **kwargs):
        self._cleared = Cleared(
            content=content,
            colors=colors,
        )
        super().__init__(
            content=self._cleared,
            *args, **kwargs,
        )

    @property
    def colors(self):
        return self._cleared.colors

    @colors.setter
    def colors(self, colors):
        self._cleared.colors = colors

