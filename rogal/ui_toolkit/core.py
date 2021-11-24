import time

from ..collections .attrdict import DefaultAttrDict
from ..geometry import Position, Size

from ..console.core import Align


"""Console UI Toolkit core building blocks."""


class ZOrder:
    BASE = 1
    MODAL = 100


class UIElement:

    """Abstract UI element that can be layouted on a panel."""

    DEFAULT_Z_ORDER = 0
    DEFAULT_ALIGN = Align.TOP_LEFT

    def __init__(self, *, width=None, height=None, align=None):
        self._width = width
        self._height = height
        if align is None:
            align = self.DEFAULT_ALIGN
        self.align = align
        self.default_z_order = self.DEFAULT_Z_ORDER
        self.renderer = None
        self.handlers = DefaultAttrDict(dict)

    @property
    def width(self):
        """Return element's fixed width or None if whole available space should be used."""
        return self._width or 0

    def set_width(self, width):
        self._width = width

    @property
    def height(self):
        """Return element's fixed height or None if whole available space should be used."""
        return self._height or 0

    def set_height(self, height):
        self._height = height

    def get_size(self, panel):
        """Return element's size based on available panel space."""
        # TODO: Allow float values? width = .75, height = .5 of panel size?
        size = Size(
            self.width or panel.width,
            self.height or panel.height,
        )
        return size

    def get_layout_panel(self, panel):
        if not (self.width or self.height):
            return panel
        size = self.get_size(panel)
        position = panel.get_position(size, self.align)
        panel = panel.create_panel(position, size)
        return panel

    def layout(self, manager, element, panel, z_order):
        z_order = z_order or self.default_z_order
        panel = self.get_layout_panel(panel)
        manager.insert(
            element,
            panel=panel,
            z_order=z_order,
            renderer=self.renderer,
        )
        manager.bind(
            element,
            **self.handlers,
        )
        if self.handlers:
            manager.grab_focus(element)

        return self.layout_content(manager, element, panel, z_order)

    def layout_content(self, manager, parent, panel, z_order):
        return z_order


class Container:

    """Mixin for UIElements containers with multiple child elements."""

    def __init__(self, content=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = list(content or [])

    def append(self, element):
        self.content.append(element)

    def extend(self, elements):
        self.content.extend(elements)

    def layout_content(self, manager, parent, panel, z_order):
        raise NotImplementedError()

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        yield from self.content


class Renderer:

    """Mixin for UIElements that renders it's contents on panel."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = self

    def render(self, panel, timestamp):
        raise NotImplementedError()


class Animated:

    """Mixin for UIElements which appearance depends on timestamp."""

    def __init__(self, duration=None, frame_duration=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._duration = duration
        self._frame_duration = frame_duration
        self._frames_num = None

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


class PostProcessed:

    """Adds list of post_renderers that will alter alter already rendered element."""

    def __init__(self, post_renderers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

