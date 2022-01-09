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

    def __init__(self, content, padding, *, align=None, width=None, height=None):
        super().__init__(
            content=content,
            align=align,
            width=width,
            height=height,
        )
        self.padding = padding or Padding.ZERO
        # TODO: Need to rework default_z_order!
        self.default_z_order = self.content.default_z_order

    @property
    def padding(self):
        return self.style.padding

    @padding.setter
    def padding(self, padding):
        self.style.padding = padding

    @containers.Bin.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        width = self.content.width
        if width:
            return width + self.padding.left + self.padding.right
        return self.FULL_SIZE

    @containers.Bin.height.getter
    def height(self):
        if self.style.height is not None:
            return self.style.height
        height = self.content.height
        if height:
            return height + self.padding.top + self.padding.bottom
        return self.FULL_SIZE

    def get_size(self, available):
        width = self.style.width
        if width is None:
            width = self.content.width
        if not width:
            width = available.width - self.padding.left - self.padding.right
        height = self.style.height
        if height is None:
            height = self.content.height
        if not height:
            height = available.height - self.padding.top - self.padding.bottom
        size = Size(width, height)
        return size

    def get_layout_panel(self, panel):
        size = self.get_size(panel)
        position = panel.get_position(size, self.align, self.padding)
        panel = panel.create_panel(position, size)
        return panel


class WithPaddedContent:

    # NOTE: You might just want to subclass Padded instead of using WithPaddedContent and Bin
    #       If you put Padded inside Bin, then Bin will get panel of content size + padding!

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
        self._padded.padding = padding
        # TODO: self.redraw() ?


class Framed(containers.Bin):

    """Renders frame around content."""

    def __init__(self, content, frame, *, align=None, width=None, height=None):
        super().__init__(
            content=content,
            align=align,
            width=width,
            height=height,
        )
        self.frame = frame
        # TODO: Consider using multiple nested frames?

    @containers.Bin.width.getter
    def width(self):
        if self.style.width is not None:
            return self.style.width
        width = self.content.width
        if width:
            return width + self.frame.extents.width
        return self.FULL_SIZE

    @containers.Bin.height.getter
    def height(self):
        if self.style.height is not None:
            return self.style.height
        height = self.content.height
        if height:
            return height + self.frame.extents.height
        return self.FULL_SIZE

    def layout_content(self, manager, parent, panel, z_order):
        element = manager.create_child(parent)
        self.frame.layout(manager, element, panel, z_order+1)
        element = manager.create_child(parent)
        panel = self.frame.get_inner_panel(panel)
        return self.content.layout(manager, element, panel, z_order+2)


class WithFramedContent:

    def __init__(self, content, frame,
                 align=None, width=None, height=None, *args, **kwargs):
        self._framed = Framed(
            content=content,
            frame=frame,
            align=align,
            width=width,
            height=height,
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
        # TODO: self.redraw() ?


class Cleared(containers.Bin):

    """Clears content area."""

    def __init__(self, content, colors, *, align=None, width=None, height=None):
        super().__init__(
            content=content,
            align=align,
            width=width,
            height=height,
        )
        self.style.update(
            colors=colors,
        )
        self.renderer = renderers.ClearPanel(
            colors=self.style.colors,
        )

    @property
    def colors(self):
        return self.style.colors

    @colors.setter
    def colors(self, colors):
        self.style.colors = colors
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
        self.post_renderer = renderers.Chain(post_renderers)

    def layout_content(self, manager, parent, panel, z_order):
        z_order = super().layout_content(manager, parent, panel, z_order)
        element = manager.create_child(parent)
        z_order += 1
        manager.insert(
            element,
            panel=panel,
            z_order=z_order,
            renderer=self.post_renderer,
        )
        return z_order

    @property
    def post_renderers(self):
        return self.post_renderer.renderers

    @post_renderers.setter
    def post_renderers(self, post_renderers):
        self.post_renderer.renderers = post_renderers or []


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
        # TODO: self.redraw() ?


# TODO: Consider: Positioned(content, position), need move(vector) and maybe move_to(position)

