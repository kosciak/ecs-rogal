import time

from ..collections.attrdict import AttrDict, DefaultAttrDict
from ..geometry import Position, Size

from ..console.core import Align


"""Console UI Toolkit core building blocks."""


class ZOrder:
    BASE = 1
    MODAL = 100


class Styled:

    def __init__(self, style=None):
        self.style = AttrDict()
        if style is not None:
            self.set_style(**style)

    def set_style(self, **style):
        self.style.update(style)


# TODO: Renderable


class UIElement(Styled):

    """Abstract UI element that can be layouted on a panel."""

    DEFAULT_ALIGN = Align.TOP_LEFT
    FULL_SIZE = 0
    DEFAULT_Z_ORDER = 0

    # def __init__(self, *, align=None, width=None, height=None):
    def __init__(self, *, renderer=None, **style):
        if not hasattr(self, 'renderer'):
            self.renderer = renderer
        super().__init__(style)
        # self.style.update(
        #     align=align,
        #     width=width,
        #     height=height,
        # )
        # TODO: get rid of default_z_order, it doesn't make much sense...
        self.default_z_order = self.DEFAULT_Z_ORDER
        # TODO: Move event_handlers to separate class/mixin?
        self.events_handlers = DefaultAttrDict(list)
        # TODO: Store element, panel or offset/size?

    def set_style(self, *, align=None, width=None, height=None, **style):
        if align is None:
            align = self.DEFAULT_ALIGN
        self.style.update(
            align=align,
            width=width, height=height,
        )

    def update_style(self, style):
        for key in ['align', 'width', 'height']:
            if key in style:
                self.style[key] = style[key]

    @property
    def align(self):
        if self.style.align is not None:
            return self.style.align
        return self.DEFAULT_ALIGN

    @property
    def width(self):
        """Return element's fixed width or 0 if whole available space should be used."""
        return self.style.width or self.FULL_SIZE

    @property
    def height(self):
        """Return element's fixed height or 0 if whole available space should be used."""
        return self.style.height or self.FULL_SIZE

    @property
    def min_width(self):
        """Minimal total width (for example width+padding)."""
        return self.width

    @property
    def min_height(self):
        """Minimal total height (for example height+padding)."""
        return self.height

    def get_size(self, available):
        """Return element's size based on available space."""
        # TODO: Allow float values? width = .75, height = .5 of available size?
        size = Size(
            self.width or available.width,
            self.height or available.height,
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
        # TODO: Split creation/insertion and layout (as just positioning on panel)?
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
            **self.events_handlers,
        )
        if self.events_handlers:
            # TODO: Not sure about this...
            #       No need to grab focus for mouse only handlers
            manager.grab_focus(element)

        return self.layout_content(manager, element, panel, z_order)

    def layout_content(self, manager, parent, panel, z_order):
        return z_order


class Container:

    """Mixin for UIElements containers with multiple child elements."""

    def __init__(self, content=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = []
        if isinstance(content, (list, tuple)):
            self.extend(content)
        elif content is not None:
            self.append(content)

    def append(self, element):
        self.content.append(element)

    def extend(self, elements):
        self.content.extend(elements)

    def remove(self, element):
        self.content.remove(element)

    def layout_content(self, manager, parent, panel, z_order):
        raise NotImplementedError()

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        yield from self.content


class Renderer(Styled):

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

