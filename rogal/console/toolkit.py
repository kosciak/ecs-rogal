import time

from ..geometry import Position, Size, WithSizeMixin
from ..utils .attrdict import DefaultAttrDict

from .core import Align, Padding


"""Console UI basic widgets and renderers toolkit."""

'''
TODO:
- progress bars (paint background only and print tiles)

'''


class UIElement:

    """Abstract UI element that can be layouted on panel."""

    DEFAULT_Z_ORDER = 0

    def __init__(self):
        self.renderer = None
        self.handlers = DefaultAttrDict(dict)

    def get_layout_panel(self, panel):
        return panel

    def layout(self, manager, widget, panel, z_order):
        z_order = z_order or self.DEFAULT_Z_ORDER
        panel = self.get_layout_panel(panel)
        manager.insert(
            widget,
            panel=panel,
            z_order=z_order,
            renderer=self.renderer,
        )

        manager.bind(
            widget,
            **self.handlers,
        )
        if self.handlers:
            manager.grab_focus(widget)

        return self.layout_content(manager, widget, panel, z_order)

    def layout_content(self, manager, parent, panel, z_order):
        return z_order


class Widget(WithSizeMixin, UIElement):

    """UI element with with it's own size, alignment and padding.

    NOTE: Subclasses MUST provide size attribute!

    """

    __slots__ = ('align', 'padding', )

    def __init__(self, *, align=Align.TOP_LEFT, padding=Padding.ZERO, **kwargs):
        super().__init__(**kwargs)
        self.align = align
        self.padding = padding

    @property
    def padded_width(self):
        return self.width + self.padding.left + self.padding.right

    @property
    def padded_height(self):
        return self.height + self.padding.top + self.padding.bottom

    @property
    def padded_size(self):
        return Size(self.padded_width, self.padded_height)

    def get_layout_panel(self, panel):
        position = panel.get_position(self.size, self.align, self.padding)
        panel = panel.create_panel(position, self.size)
        return panel


class Container(UIElement):

    """UIElements container.

    Widgets are rendered in FIFO order and each widget use whole panel.
    Will overdraw previous ones if they overlap.

    """

    def __init__(self, widgets=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = list(widgets or [])

    def layout_content(self, manager, parent, panel, z_order):
        z_order = self.layout_children(manager, parent, panel, z_order+1)
        return z_order

    def layout_children(self, manager, parent, panel, z_order):
        # Return highest z_order of all children
        return z_order

    def append(self, widget):
        self.children.append(widget)

    def extend(self, widgets):
        self.children.extend(widgets)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        yield from self.children


class Renderer:

    """Abstract UI element that can render it's contents on panel."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = self

    def render(self, panel):
        raise NotImplementedError()


class PostPorcessed:

    def __init__(self, post_renderers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_renderers = list(post_renderers or [])

    def layout_content(self, manager, parent, panel, z_order):
        z_order = super().layout_content(manager, parent, panel, z_order)
        for renderer in self.post_renderers:
            widget = manager.create_child(parent)
            z_order += 1
            manager.insert(
                widget,
                panel=panel,
                z_order=z_order,
                renderer=renderer,
            )
        return z_order


class Cursor(Renderer, UIElement):

    def __init__(self, *, glyph=None, colors=None, position=None, blinking=None):
        super().__init__()
        self.glyph = glyph # NOTE: if glyph is set it will OVERWRITE character under cursor!
        self.colors = colors
        self.position = position or Position.ZERO
        if blinking:
            self.renderer = Blinking(self, rate=blinking)

    def move(self, vector):
        self.position = self.position.move(vector)

    def render(self, panel):
        if self.glyph:
            panel.print(self.glyph.char, self.position, colors=self.colors)
        elif self.colors:
            panel.paint(self.colors, self.position)
        else:
            panel.invert(self.position)


class Text(Renderer, Widget):

    """Text widget and renderer."""

    def __init__(self, txt, width=None, colors=None, *, align=Align.TOP_LEFT, padding=Padding.ZERO):
        super().__init__(align=align, padding=padding)
        self.txt = txt
        self.colors = colors

        lines = self.txt.splitlines() or ['', ]
        self.txt_size = Size(
            max(len(line) for line in lines),
            len(lines)
        )
        self.size = Size(
            max(width or 0, self.txt_size.width),
            len(lines)
        )

    def get_layout_panel(self, panel):
        panel = panel.create_panel(Position.ZERO, Size(panel.width, self.padded_height))
        # position = panel.get_position(self.size, self.align)
        # panel = panel.create_panel(position, self.size)
        return panel

    def render(self, panel):
        if self.colors:
            panel.clear(self.colors)
        position = panel.get_align_position(self.txt_size, self.align, self.padding)
        panel.print(self.txt, position, colors=self.colors, align=self.align)

