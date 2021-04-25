import time

from ..geometry import Position, Size, WithSizeMixin
from ..utils .attrdict import DefaultAttrDict

from .core import Align


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

    """UI element with with it's own size and alignment.

    NOTE: Subclasses MUST provide size attribute!

    """

    __slots__ = ('align', )

    def __init__(self, *, align=None, **kwargs):
        super().__init__(**kwargs)
        if align is None:
            self.align = Align.TOP_LEFT
        else:
            self.align = align

    def get_layout_panel(self, panel):
        position = panel.get_position(self.size, self.align)
        panel = panel.create_panel(position, self.size)
        return panel


class Container(UIElement):

    """UIElements container.

    Widgets are rendered in FIFO order and each widget use whole panel.
    Will overdraw previous ones if they overlap.

    """

    def __init__(self, content=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = list(content or [])

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

