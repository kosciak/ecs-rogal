import collections

from ..geometry import Position, Size, WithSizeMixin
from ..tiles import Tile

from .core import Align, Padding


"""Console UI basic widgets and renderers toolkit."""

'''
TODO:
How it should work:
- create window with all the widgets
- call layout and create renderers entities
- render called by system, need Z-order to sort what to render first!

'''


def get_x(panel_width, width, align, padding=Padding.ZERO):
    if align & Align.RIGHT:
        x = panel_width - width - padding.right
    elif align & Align.CENTER:
        x = panel_width//2 - width//2 - padding.right + padding.left
    else:
        x = padding.left
    return x


def get_align_x(panel_width, width, align, padding=Padding.ZERO):
    if align & Align.RIGHT:
        x = panel_width - padding.right - 1
    elif align & Align.CENTER:
        x = panel_width//2 - padding.right + padding.left
    else:
        x = padding.left
    return x


def get_y(panel_height, height, align, padding=Padding.ZERO):
    if align & Align.TOP:
        y = padding.top
    elif align & Align.BOTTOM:
        y = panel_height - height - padding.bottom
    elif align & Align.MIDDLE:
        y = panel_height//2 - height//2 - padding.bottom + padding.top
    else:
        y = padding.top
    return y


def get_position(panel, size, align, padding=Padding.ZERO):
    return Position(
        get_x(panel.width, size.width, align, padding),
        get_y(panel.height, size.height, align, padding)
    )


def get_align_position(panel, size, align, padding=Padding.ZERO):
    return Position(
        get_align_x(panel.width, size.width, align, padding),
        get_y(panel.height, size.height, align, padding)
    )


class Renderer(WithSizeMixin):

    def __init__(self, panel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Z-order ??
        self._panel = None
        self.size = None
        self.panel = panel

    @property
    def panel(self):
        return self._panel

    @panel.setter
    def panel(self, panel):
        self._panel = panel
        self.size = self._panel and self._panel.size

    def clear(self, colors):
        self.panel.clear(colors)

    def layout(self, panel):
        self.panel = panel
        yield self

    def render(self):
        raise NotImplementedError()


class Widget(WithSizeMixin):

    __slots__ = ('align', 'padding', )

    def __init__(self, align, padding=Padding.ZERO, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.align = align
        self.padding = padding
        # NOTE: subclasses MUST provide size!

    def layout(self, panel):
        """Yield Renderer instances."""
        yield from ()


class Container:

    def __init__(self, widgets=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = list(widgets or [])

    def append(self, widget):
        self.widgets.append(widget)

    def __len__(self):
        return len(self.widgets)

    def __iter__(self):
        yield from self.widgets



class DecorationsRenderer(Renderer):

    def __init__(self, panel, decorations):
        super().__init__(panel)
        self.decorations = decorations

    def render(self):
        self.panel.draw(self.decorations.top, Position(1, 0), Size(self.width-2, 1))
        self.panel.draw(self.decorations.bottom, Position(1, self.height-1), Size(self.width-2, 1))
        self.panel.draw(self.decorations.left, Position(0, 1), Size(1, self.height-2))
        self.panel.draw(self.decorations.right, Position(self.width-1, 1), Size(1, self.height-2))

        self.panel.draw(self.decorations.top_left, Position(0, 0))
        self.panel.draw(self.decorations.top_right, Position(self.width-1, 0))
        self.panel.draw(self.decorations.bottom_left, Position(0, self.height-1))
        self.panel.draw(self.decorations.bottom_right, Position(self.width-1, self.height-1))


class Decorations(WithSizeMixin):

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

    def layout(self, panel):
        yield DecorationsRenderer(panel, self)

    def __nonzero__(self):
        return any(self.top, self.bottom, self.left, self.right)


class Text(Widget, Renderer):

    def __init__(self, txt, width=None, colors=None, *, align=Align.TOP_LEFT, padding=Padding.ZERO):
        super().__init__(align=align, padding=padding)
        self.txt = txt
        self.colors = colors

        lines = self.txt.splitlines()
        self.txt_size = Size(
            max(len(line) for line in lines),
            len(lines)
        )
        self.size = Size(
            max(width or 0, self.txt_size.width),
            len(lines)
        )

    def layout(self, panel):
        self.panel = panel.create_panel(Position.ZERO, Size(panel.width, self.height))
        yield self

    def render(self):
        position = get_align_position(self.panel, self.txt_size, self.align)
        self.panel.print(self.txt, position, colors=self.colors, align=self.align)


class Decorated(Widget):

    def __init__(self, content, decorations, *, align, padding=Padding.ZERO):
        super().__init__(align, padding)
        self.content = content
        self.decorations = decorations

        self.size = Size(
            self.content.width + self.decorations.width,
            self.content.height + self.decorations.height
        )

    def layout(self, panel):
        position = get_position(panel, self.size, self.align, self.padding)
        panel = panel.create_panel(position, self.size)
        yield from self.decorations.layout(panel)
        panel = self.decorations.inner_panel(panel)
        yield from self.content.layout(panel)


class Row(Container, Widget):

    def __init__(self, widgets=None, *, align, padding=Padding.ZERO):
        super().__init__(widgets=widgets, align=align, padding=padding)
        # align=LEFT    |AA BB CC      |
        # align=RIGHT   |      AA BB CC|
        # align=CENTER  |   AA BB CC   |

    @property
    def size(self):
        if not self:
            return None
        return Size(
            # TODO: widget.padding?
            sum([widget.width for widget in self]),
            max([widget.height for widget in self])
        )

    def layout(self, panel):
        position = get_position(panel, self.size, self.align, self.padding)
        for widget in self:
            # TODO: widget.padding?
            subpanel = panel.create_panel(position, widget.size)
            yield from widget.layout(subpanel)
            position += Position(widget.width, 0)


class Split(Container):

    def __init__(self, widget=None, *, left=None, right=None, top=None, bottom=None):
        super().__init__(widgets)
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def layout(self, panel):
        panels = panel.split(self.left, self.right, self.top, self.bottom)
        for i, widget in enumerate(self.widgets):
            yield from widget.layout(panels[i])
            if i >= 2:
                break


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass

