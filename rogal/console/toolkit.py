import collections
import time

from ..geometry import Position, Size, WithSizeMixin
from ..tiles import Tile
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


class Renderer:

    """Abstract UI element that can render it's contents on panel."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = self

    def render(self, panel):
        raise NotImplementedError()


class ClearPanel(Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel):
        panel.clear(self.colors)


class PaintPanel(Renderer):

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    def render(self, panel):
        panel.paint(self.colors, Position.ZERO, panel.size)


class InvertColors(Renderer):

    def render(self, panel):
        panel.invert(Position.ZERO, panel.size)


# TODO: RenderEffect?
class Blinking(Renderer):

    BLINK_RATE = 1200

    def __init__(self, renderer, rate=BLINK_RATE):
        super().__init__()
        self._renderer = renderer
        self.rate = rate // 2

    def render(self, panel):
        # TODO: blinking MUST be synchronized (during a frame) between ALL renderers!
        #       Maybe should be done on System level? NOT calling render if Blinking component present?
        # rate < 0 should mean inverted blinking
        if int((time.time()*1000) / self.rate) % 2 == 0:
            return
        return self._renderer.render(panel)


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


class Widget(WithSizeMixin, UIElement):

    """UI element with with it's own size, alignment and padding.

    NOTE: Subclasses MUST provide size attribute!

    """

    __slots__ = ('align', 'padding', )

    def __init__(self, align=Align.TOP_LEFT, padding=Padding.ZERO, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class Decorations(WithSizeMixin, Renderer, UIElement):

    """Frame decorations."""

    __slots__ = (
        'top', 'bottom', 'left', 'right',
        '_top_left', '_top_right', '_bottom_left', '_bottom_right',
        'inner_offset', 'size',
    )

    def __init__(self,
        left=None, right=None,
        top=None, bottom=None,
        top_left=None, top_right=None,
        bottom_left=None, bottom_right=None,
        *, colors=None,
    ):
        super().__init__()
        self.top = Tile.create(top, fg=colors and colors.fg, bg=colors and colors.bg)
        self.bottom = Tile.create(bottom, fg=colors and colors.fg, bg=colors and colors.bg)
        self.left = Tile.create(left, fg=colors and colors.fg, bg=colors and colors.bg)
        self.right = Tile.create(right, fg=colors and colors.fg, bg=colors and colors.bg)
        self._top_left = Tile.create(top_left, fg=colors and colors.fg, bg=colors and colors.bg)
        self._top_right = Tile.create(top_right, fg=colors and colors.fg, bg=colors and colors.bg)
        self._bottom_left = Tile.create(bottom_left, fg=colors and colors.fg, bg=colors and colors.bg)
        self._bottom_right = Tile.create(bottom_right, fg=colors and colors.fg, bg=colors and colors.bg)

        self.inner_offset = Position(
            self.left and 1 or 0,
            self.top and 1 or 0,
        )
        self.size = Size(
            self.inner_offset.x + (self.right and 1 or 0),
            self.inner_offset.y + (self.bottom and 1 or 0)
        )

    @property
    def top_left(self):
        return self._top_left or self.top or self.left

    @property
    def top_right(self):
        return self._top_right or self.top or self.right

    @property
    def bottom_left(self):
        return self._bottom_left or self.bottom or self.left

    @property
    def bottom_right(self):
        return self._bottom_right or self.bottom or self.right

    def update(self, colors=None, **kwargs):
        return Decorations(
            kwargs.get('top', self.top), kwargs.get('bottom', self.bottom),
            kwargs.get('left', self.left), kwargs.get('right', self.right),
            kwargs.get('top_left', self._top_left), kwargs.get('top_right', self._top_right),
            kwargs.get('bottom_left', self._bottom_left), kwargs.get('bottom_right', self._bottom_right),
            colors=colors,
        )

    def inner_panel(self, panel):
        return panel.create_panel(
            self.inner_offset,
            Size(panel.width-self.width, panel.height-self.height)
        )

    def render(self, panel):
        panel.draw(self.top, Position(1, 0), Size(panel.width-2, 1))
        panel.draw(self.bottom, Position(1, panel.height-1), Size(panel.width-2, 1))
        panel.draw(self.left, Position(0, 1), Size(1, panel.height-2))
        panel.draw(self.right, Position(panel.width-1, 1), Size(1, panel.height-2))

        panel.draw(self.top_left, Position(0, 0))
        panel.draw(self.top_right, Position(panel.width-1, 0))
        panel.draw(self.bottom_left, Position(0, panel.height-1))
        panel.draw(self.bottom_right, Position(panel.width-1, panel.height-1))

    def __nonzero__(self):
        return any(self.top, self.bottom, self.left, self.right)


# TODO: Rename to Frame?
class Decorated(Widget):

    """Decorations with element rendered inside of them."""

    def __init__(self, decorations, decorated, *, align=Align.TOP_LEFT, padding=Padding.ZERO):
        super().__init__(align=align, padding=padding)
        self.decorations = decorations
        self.decorated = decorated

        size = getattr(self.decorated, 'size', None)
        self.size = size and Size(
            self.decorated.padded_width + self.decorations.width,
            self.decorated.padded_height + self.decorations.height
        )

    def get_layout_panel(self, panel):
        size = self.size or panel.size
        position = panel.get_position(size, self.align, self.padding)
        panel = panel.create_panel(position, size)
        return panel

    def layout_content(self, manager, parent, panel, z_order):
        widget = manager.create_child(parent)
        self.decorations.layout(manager, widget, panel, z_order+1)
        widget = manager.create_child(parent)
        panel = self.decorations.inner_panel(panel)
        return self.decorated.layout(manager, widget, panel, z_order+2)

