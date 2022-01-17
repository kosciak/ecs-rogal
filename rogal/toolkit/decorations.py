from ..geometry import Position, Size

from ..console.core import Padding

from . import core
from . import basic
from . import containers
from . import renderers


"""UIElements that wrap it's content and change its look.

<Decorated> class function as decorator around content.
With<Decorated>Content is a mixin that exposes decorator attributes/methods.

This way you can easily contruct more complex elements by stacking decorations.

"""


class Padded(containers.Bin):

    """Adds padding to it's content."""

    DEFAULT_PADDING = Padding.ZERO

    def set_style(self, *, padding=None, **kwargs):
        if padding is None:
            padding = self.DEFAULT_PADDING
        self.style.update(
            padding=padding,
        )
        super().set_style(**kwargs)

    @property
    def padding(self):
        return self.style.padding

    @property
    def min_width(self):
        width = self.width
        if width:
            return width + self.padding.left + self.padding.right
        return self.FULL_SIZE

    @property
    def min_height(self):
        height = self.height
        if height:
            return height + self.padding.top + self.padding.bottom
        return self.FULL_SIZE

    def get_size(self, available):
        width = self.width
        if not width:
            width = available.width - self.padding.left - self.padding.right
        height = self.height
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

    def __init__(self, content, **kwargs):
        self._padded = Padded(
            content=content,
        )
        super().__init__(
            content=self._padded,
            **kwargs,
        )

    def set_style(self, *, padding=None, **style):
        self._padded.set_style(
            colors=colors,
        )
        super().set_style(**style)

    @property
    def padding(self):
        return self._padded.padding


class Framed(containers.Bin):

    """Renders frame around content."""

    def __init__(self, content, **kwargs):
        self.frame = basic.Frame()
        super().__init__(
            content=content,
            **kwargs,
        )
        # TODO: Consider using multiple nested frames?

    def set_style(self, Frame=None, **style):
        Frame = Frame or {} # TODO: if Frame is not None: ???
        self.frame.set_style(**Frame)
        super().set_style(**style)

    @property
    def width(self):
        if self.style.width is not None:
            return self.style.width
        width = self.content.min_width
        if width:
            return width + self.frame.extents.width
        return self.FULL_SIZE

    @property
    def height(self):
        if self.style.height is not None:
            return self.style.height
        height = self.content.min_height
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

    def __init__(self, content, **kwargs):
        self._framed = Framed(
            content=content,
        )
        super().__init__(
            content=self._framed,
            **kwargs,
        )

    def set_style(self, Frame=None, **style):
        self._framed.set_style(
            Frame=Frame,
        )
        super().set_style(**style)

    @property
    def frame(self):
        return self._framed.frame


class Cleared(core.Renderable, containers.Bin):

    """Clears content area."""

    def __init__(self, content, **kwargs):
        super().__init__(
            content=content,
            renderer=renderers.ClearPanel(),
            **kwargs,
        )

    def set_style(self, *, colors=None, **style):
        self.renderer.set_style(
            colors=colors,
        )
        super().set_style(**style)

    @property
    def colors(self):
        return self.renderer.style.colors


class WithClearedContent:

    def __init__(self, content, **kwargs):
        self._cleared = Cleared(
            content=content,
        )
        super().__init__(
            content=self._cleared,
            **kwargs,
        )

    def set_style(self, *, colors=None, **style):
        self._cleared.set_style(
            colors=colors,
        )
        super().set_style(**style)

    @property
    def colors(self):
        return self._cleared.colors


class PostProcessed(containers.Bin):

    """Adds list of post_renderers that alter already rendered element."""

    def __init__(self, content, post_renderers=None):
        # TODO: Store it style somehow
        self.post_renderer = renderers.Chain(post_renderers)
        super().__init__(
            content=content,
        )

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

    def __init__(self, content, *, post_renderers=None, **kwargs):
        self._post_processed = PostProcessed(
            content=content,
            post_renderers=post_renderers,
        )
        super().__init__(
            content=self._post_processed,
            **kwargs,
        )

    @property
    def post_renderers(self):
        return self._post_processed.post_renderers

    @post_renderers.setter
    def post_renderers(self, post_renderers):
        self._post_processed.post_renderers = post_renderers
        # TODO: self.redraw() ?


# TODO: Consider: Positioned(content, position), need move(vector) and maybe move_to(position)

