from ..geometry import Position, Size
from ..tiles import Tile

from . import toolkit


"""Widgets that wrap other widget and change their look."""


class Padded(toolkit.Widget):

    def __init__(self, content, padding, *, align=None, **kwargs):
        # TODO: use content.align instead of align in constructor? OR align=align or content.align?
        super().__init__(align=align or content.align, **kwargs)
        self.content = content
        self.default_z_order = self.content.DEFAULT_Z_ORDER
        self.padding = padding

    @property
    def width(self):
        width = self.content.width
        return width and (width + self.padding.left + self.padding.right) or 0

    @property
    def height(self):
        height = self.content.height
        return height and (height + self.padding.top + self.padding.bottom) or 0

    def get_inner_panel(self, panel):
        position = Position(self.padding.left, self.padding.top)
        size = Size(
            panel.width - self.padding.left - self.padding.right,
            panel.height - self.padding.top - self.padding.bottom,
        )
        return panel.create_panel(position, size)

    def layout_content(self, manager, parent, panel, z_order):
        widget = manager.create_child(parent)
        panel = self.get_inner_panel(panel)
        return self.content.layout(manager, widget, panel, z_order+1)

    def layout(self, manager, widget, panel, z_order):
        return super().layout(manager, widget, panel, z_order or self.default_z_order)



# TODO: Only Renderer set as renderer for Framed? What about Button that subclasses it?
class Frame(toolkit.Renderer, toolkit.UIElement):

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
        self.extents = Size(
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
        return Frame(
            kwargs.get('top', self.top), kwargs.get('bottom', self.bottom),
            kwargs.get('left', self.left), kwargs.get('right', self.right),
            kwargs.get('top_left', self._top_left), kwargs.get('top_right', self._top_right),
            kwargs.get('bottom_left', self._bottom_left), kwargs.get('bottom_right', self._bottom_right),
            colors=colors,
        )

    def inner_panel(self, panel):
        return panel.create_panel(
            self.inner_offset,
            Size(panel.width-self.extents.width, panel.height-self.extents.height)
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


class Framed(toolkit.Widget):

    """Frame with element rendered inside."""

    def __init__(self, content, frame, *, align=None):
        super().__init__(align=align)
        self.content = content
        self.frame = frame

    @property
    def width(self):
        width = self.content.width
        return width and (width + self.frame.extents.width) or 0

    @property
    def height(self):
        height = self.content.height
        return height and (height + self.frame.extents.height) or 0

    def layout_content(self, manager, parent, panel, z_order):
        widget = manager.create_child(parent)
        self.frame.layout(manager, widget, panel, z_order+1)
        widget = manager.create_child(parent)
        panel = self.frame.inner_panel(panel)
        return self.content.layout(manager, widget, panel, z_order+2)

