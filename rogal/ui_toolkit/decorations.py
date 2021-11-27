from ..geometry import Position, Size

from ..console.core import Padding

from . import core
from . import containers
from . import renderers


"""UIElements that wrap it's content and change its look.

<Decorated> class function as decorator around content.
With<Decorated>Content is a mixin that exposes decorator attributes/methods.

This way you can easily contruct more complex elements by stacking decorations.

"""


class Padded(containers.Bin):

    """Adds padding to it's content."""

    def __init__(self, content, padding, *, align=None):
        self.padding = padding or Padding.ZERO
        super().__init__(
            content=content,
            align=align,
        )
        self.default_z_order = self.content.default_z_order

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
            align=align,
            *args, **kwargs,
        )

    @property
    def padding(self):
        return self._padded.padding

    @padding.setter
    def padding(self, padding):
        self._padded.frame = padding


class Framed(containers.Bin):

    """Renders frame around content."""

    def __init__(self, content, frame, *, align=None):
        self.frame = frame
        super().__init__(
            content=content,
            align=align,
        )
        # TODO: Consider using multiple frames?

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
            align=align,
            *args, **kwargs,
        )

    @property
    def frame(self):
        return self._framed.frame

    @frame.setter
    def frame(self, frame):
        self._framed.frame = frame


class Cleared(containers.Bin):

    """Clears content area."""

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


class PostProcessed(containers.Bin):

    """Adds list of post_renderers that alter already rendered element."""

    def __init__(self, content, post_renderers=None):
        super().__init__(
            content=content,
        )
        self.post_renderers = list(post_renderers or [])

    def layout_content(self, manager, parent, panel, z_order):
        z_order = super().layout_content(manager, parent, panel, z_order)
        for renderer in self.post_renderers:
            element = manager.create_child(parent)
            z_order += 1
            manager.insert(
                element,
                panel=panel,
                z_order=z_order,
                renderer=renderer,
            )
        return z_order


class WithPostProcessedContent:

    def __init__(self, content, post_renderers=None, *args, **kwargs):
        self._post_processed = PostProcessed(
            content=content,
            post_renderers=post_renderers,
        )
        super().__init__(
            content=self._post_processed,
            *args, **kwargs,
        )

    @property
    def post_renderers(self):
        return self._post_processed.post_renderers

    @post_renderers.setter
    def post_renderers(self, post_renderers):
        self._post_processed.post_renderers = post_renderers


# TODO: Consider Positioned(content, position)

