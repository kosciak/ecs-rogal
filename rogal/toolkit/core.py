import time

from ..collections.attrdict import AttrDict
from ..geometry import Position, Size

from ..console.core import Align


"""Console UI Toolkit core building blocks."""


class ZOrder:
    BASE = 1
    MODAL = 100


class UIElement:

    """Base UI element."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.element = None

    def insert(self, manager, element):
        self.element = element


class Layoutable(UIElement):

    """Base class for elements that can be layouted on the panel."""

    def layout(self, manager, panel, z_order):
        manager.insert(
            self.element,
            panel=panel,
            z_order=z_order,
        )
        return panel, z_order


class Styled:

    """Mixin for styles and stylesheets integration."""

    def __init__(self, *, selector=None, style=None, **kwargs):
        super().__init__(**kwargs)
        self.style = AttrDict()
        # NOTE: call set_style even if style is None for defaults to be set correctly
        style = style or {}
        self.set_style(**style)

    def set_style(self, **style):
        self.style.update(style)


class WithColors(Styled):

    def set_style(self, *, colors=None, **style):
        self.style.update(
            colors=colors,
        )
        super().set_style(**style)

    @property
    def colors(self):
        return self.style.colors


class WithSize(Styled, Layoutable):

    """Layoutable based on width/height and align."""

    DEFAULT_Z_ORDER = 0
    DEFAULT_ALIGN = Align.TOP_LEFT
    FULL_SIZE = 0 # TODO: Consider changing to -1
    DEFAULT_WIDTH = FULL_SIZE
    DEFAULT_HEIGHT = FULL_SIZE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: get rid of default_z_order, it doesn't make much sense...
        self.default_z_order = self.DEFAULT_Z_ORDER

    def set_style(self, *, align=None, width=None, height=None, **style):
        # if align is None:
        #     align = self.DEFAULT_ALIGN
        self.style.update(
            align=align,
            width=width, height=height,
        )

    @property
    def align(self):
        align = self.style.align
        if align is None:
            align = self.DEFAULT_ALIGN
        return align

    @property
    def width(self):
        """Return element's fixed width or 0 if whole available space should be used."""
        return self.style.width or self.DEFAULT_WIDTH

    @property
    def height(self):
        """Return element's fixed height or 0 if whole available space should be used."""
        return self.style.height or self.DEFAULT_HEIGHT

    @property
    def min_width(self):
        """Minimal total width (for example width+padding)."""
        return self.width

    @property
    def min_height(self):
        """Minimal total height (for example height+padding)."""
        return self.height

    def _calc_size(self, size, available):
        if size == self.FULL_SIZE:
            size = available
        if size and size < 1.:
            size = round(size*available)
        return size

    def get_width(self, available):
        return self._calc_size(self.width, available)

    def get_height(self, available):
        return self._calc_size(self.height, available)

    def get_size(self, available):
        """Return element's size based on available space."""
        size = Size(
            self.get_width(available.width),
            self.get_height(available.height),
        )
        return size

    def get_layout_panel(self, panel):
        size = self.get_size(panel)
        if not size == panel.size:
            position = panel.get_position(size, self.align)
            panel = panel.create_panel(position, size)
        return panel

    def layout(self, manager, panel, z_order):
        z_order = z_order or self.default_z_order
        panel = self.get_layout_panel(panel)
        manager.insert(
            self.element,
            panel=panel,
            z_order=z_order,
        )
        return panel, z_order


class Renderable:

    """Mixin for elements with renderer."""

    def __init__(self, *, renderer, **kwargs):
        self.renderer = renderer
        super().__init__(**kwargs)

    def insert(self, manager, element):
        super().insert(manager, element)
        manager.insert(
            element,
            renderer=self.renderer,
        )


class Renderer(Renderable, Layoutable):

    """Mixin for elements that render it's contents on a panel."""

    def __init__(self, **kwargs):
        super().__init__(
            renderer=self,
            **kwargs,
        )

    def render(self, panel, timestamp):
        raise NotImplementedError()


class Container:

    """Mixin for containers with child element(s)."""

    def insert(self, manager, element):
        super().insert(manager, element)
        for child in self:
            if child.element:
                continue
            child.insert(
                manager,
                manager.create_child(element),
            )

    def layout(self, manager, panel, z_order):
        panel, z_order = super().layout(manager, panel, z_order)
        z_order = self.layout_content(manager, panel, z_order)
        return panel, z_order

    def layout_content(self, manager, panel, z_order):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()


class Animated:

    """Mixin for elements which appearance depends on timestamp."""

    def __init__(self, *, duration=None, frame_duration=None, **kwargs):
        super().__init__(**kwargs)
        # TODO: Store settings in style
        self._duration = duration
        self._frame_duration = frame_duration
        self._frames_num = None
        # TODO: AnimationType: CYCLE, BOUNCE, ???
        # TODO: repeat - how many times animation should be played

    def get_frames_num(self):
        raise NotImplementedError()

    @property
    def frames_num(self):
        if self._frames_num is None:
            self._frames_num = self.get_frames_num()
        return self._frames_num

    @property
    def duration(self):
        if self._duration is None:
            self._duration = self.frame_duration * self.frames_num
        return self._duration

    @property
    def frame_duration(self):
        if self._frame_duration is None:
            self._frame_duration = self.duration // self.frames_num
        return self._frame_duration

    def get_frame_num(self, timestamp):
        return int(timestamp // self.frame_duration % self.frames_num)

