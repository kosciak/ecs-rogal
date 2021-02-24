import collections

from ..geometry import Position, Size, WithSizeMixin
from ..tiles import Tile

from .core import Align, Padding


"""Console UI basic widgets toolkit."""


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


class Widget(WithSizeMixin):

    __slots__ = ('align', 'padding', )

    def __init__(self, align, padding=Padding.ZERO):
        self.align = align
        self.padding = padding
        # NOTE: subclasses MUST provide size!

    def render(self, panel):
        return


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

    def render(self, panel):
        panel.draw(self.top, Position(1, 0), Size(panel.width-2, 1))
        panel.draw(self.bottom, Position(1, panel.height-1), Size(panel.width-2, 1))
        panel.draw(self.left, Position(0, 1), Size(1, panel.height-2))
        panel.draw(self.right, Position(panel.width-1, 1), Size(1, panel.height-2))

        panel.draw(self.top_left, Position(0, 0))
        panel.draw(self.top_right, Position(panel.width-1, 0))
        panel.draw(self.bottom_left, Position(0, panel.height-1))
        panel.draw(self.bottom_right, Position(panel.width-1, panel.height-1))

    def inner_panel(self, panel):
        return panel.create_panel(
            self.inner_offset,
            Size(panel.width-self.width, panel.height-self.height)
        )

    def __nonzero__(self):
        return any(self.top, self.bottom, self.left, self.right)


class Text(Widget):

    def __init__(self, txt, width=None, colors=None, *, align=Align.TOP_LEFT, padding=Padding.ZERO):
        super().__init__(align, padding)
        self.txt = txt
        self.colors = colors

        lines = self.txt.splitlines()
        self._size = Size(
            max(len(line) for line in lines),
            len(lines)
        )
        self.size = Size(
            max(width or 0, self._size.width),
            len(lines)
        )

    def render(self, panel):
        position = get_align_position(panel, self._size, self.align, self.padding)
        panel.print(self.txt, position, colors=self.colors, align=self.align)


class Decorated(Widget):

    def __init__(self, widget, decorations, *, align, padding=Padding.ZERO):
        super().__init__(align, padding)
        self.widget = widget
        self.decorations = decorations

        self.size = Size(
            self.widget.width + self.decorations.width,
            self.widget.height + self.decorations.height
        )

    def render(self, panel):
        position = get_position(panel, self.size, self.align, self.padding)
        panel = panel.create_panel(position, self.size)
        self.decorations.render(panel)
        panel = self.decorations.inner_panel(panel)
        # TODO: panel.clear() ?
        self.widget.render(panel)


class Row(WithSizeMixin, collections.UserList):

    def __init__(self, widgets=None, *, align, padding=Padding.ZERO):
        super().__init__(widgets)
        # align=LEFT    |AA BB CC      |
        # align=RIGHT   |      AA BB CC|
        # align=CENTER  |   AA BB CC   |
        self.align = align
        self.padding = padding

    @property
    def size(self):
        if not self:
            return None
        return Size(
            # TODO: widget.padding?
            sum([widget.width for widget in self]),
            max([widget.height for widget in self])
        )

    def render(self, panel):
        position = get_position(panel, self.size, self.align, self.padding)
        for widget in self:
            # TODO: widget.padding?
            p = panel.create_panel(position, widget.size)
            widget.render(p)
            position += Position(widget.width, 0)


# TODO: ???
# class JustifiedRow:
#     # |AA    BB    CC|
#     pass

