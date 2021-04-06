from ..geometry import Position, Vector, Size

from ..events import handlers

from .core import Align, Padding, ZOrder
from . import containers
from . import toolkit


class UIWidget:

    def __init__(self, default_colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = toolkit.ClearPanel(
            colors=default_colors,
        )
        self.widget = None
        self.manager = None

    @property
    def colors(self):
        return self.renderer.colors

    @colors.setter
    def colors(self, colors):
        self.renderer.colors = colors

    def layout(self, manager, widget, panel, z_order):
        self.manager = manager
        self.widget = widget
        manager.insert(
            widget,
            ui_widget=self,
        )
        return super().layout(manager, widget, panel, z_order)

    def redraw(self):
        self.manager.redraw(self.widget)


class TextInput(UIWidget, containers.Overlay, toolkit.Widget):

    def __init__(self, ecs, width, *,
                 default_colors,
                 default_text=None,
                 align=Align.TOP_LEFT,
                 padding=Padding.ZERO,
                ):
        super().__init__(
            align=Align.TOP_LEFT,
            padding=padding,
            default_colors=default_colors,
        )
        self.size = Size(width, 1)
        self.text = toolkit.Text(
            default_text or '',
            width=width,
        )
        self.cursor = toolkit.Cursor(
            # colors=default_colors.invert(),
            blinking=1200,
        )
        self.cursor.position = Position(len(self.txt), 0)
        self.children.extend([
            self.text,
            # TODO: Show Cursor only if has focus and ready for input?
            self.cursor,
        ])
        self.handlers = dict(
            on_text_input={
                handlers.TextInput(): self.on_input,
            },
            on_key_press={
                handlers.TextEdit(ecs): self.on_edit,
            },
            # TODO: change cursor on mouse over
        )

    @property
    def txt(self):
        return self.text.txt

    @txt.setter
    def txt(self, txt):
        self.text.txt = txt

    def on_input(self, widget, char):
        if len(self.txt) < self.width-1:
            before_cursor = self.txt[:self.cursor.position.x]
            after_cursor = self.txt[self.cursor.position.x:]
            self.txt = before_cursor + char + after_cursor
            self.cursor.move(Vector(1, 0))

    def on_edit(self, widget, cmd):
        if not cmd:
            return
        elif cmd == 'CLEAR':
            self.txt = ''
            self.cursor.position = Position.ZERO
        elif cmd == 'BACKSPACE':
            before_cursor = self.txt[:self.cursor.position.x]
            if before_cursor:
                after_cursor = self.txt[self.cursor.position.x:]
                self.txt = before_cursor[:-1] + after_cursor
                self.cursor.move(Vector(-1, 0))
        elif cmd == 'DELETE':
            after_cursor = self.txt[self.cursor.position.x:]
            if after_cursor:
                before_cursor = self.txt[:self.cursor.position.x]
                self.txt = before_cursor + after_cursor[1:]
        elif cmd == 'HOME':
            self.cursor.position = Position.ZERO
        elif cmd == 'END':
            self.cursor.position = Position(len(self.txt), 0)
        elif cmd == 'FORWARD':
            if self.cursor.position.x < len(self.txt):
                self.cursor.move(Vector(1, 0))
        elif cmd == 'BACKWARD':
            if self.cursor.position.x > 0:
                self.cursor.move(Vector(-1, 0))
        elif cmd == 'PASTE':
            pass


class Button(UIWidget, toolkit.PostPorcessed, toolkit.Decorated):

    def __init__(self, decorations, text, *,
                 on_mouse_click,
                 default_colors,
                 selected_colors=None, press_colors=None,
                 selected_renderers=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            decorations=decorations,
            decorated=text,
            align=align,
            default_colors=default_colors,
        )
        self.default_colors = default_colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])
        self.handlers = dict(
            on_mouse_click=on_mouse_click,
            on_mouse_press={
                handlers.MouseLeftButton(): self.on_press,
            },
            on_mouse_up={
                handlers.MouseLeftButton(): self.on_select,
            },
            on_mouse_in={
                handlers.MouseIn(): self.on_select,
            },
            on_mouse_over={
            },
            on_mouse_out={
                handlers.MouseOut(): self.on_unselect,
            },
        )

    @property
    def txt(self):
        return self.decorated.txt

    @txt.setter
    def txt(self, txt):
        self.decorated.txt = text

    def on_select(self, widget, value):
        self.colors = self.selected_colors
        self.post_renderers = self.selected_renderers
        self.redraw();

    def on_unselect(self, widget, value):
        self.colors = self.default_colors
        self.post_renderers = []
        self.redraw()

    def on_press(self, widget, position):
        self.colors = self.press_colors
        self.post_renderers = self.selected_renderers
        self.redraw()


class ListItem(UIWidget, toolkit.PostPorcessed, containers.Row):

    def __init__(self, index, item, *,
                 on_mouse_click,
                 default_colors,
                 selected_renderers=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            widgets=[
                index,
                item,
            ],
            align=align,
            default_colors=default_colors,
        )
        self.selected_renderers = list(selected_renderers or [])
        self.handlers = dict(
            on_mouse_click=on_mouse_click,
            on_mouse_in={
                handlers.MouseIn(): self.on_select,
            },
            on_mouse_over={
            },
            on_mouse_out={
                handlers.MouseOut(): self.on_unselect,
            },
        )

    def on_select(self, widget, value):
        self.post_renderers = self.selected_renderers
        self.redraw();

    def on_unselect(self, widget, value):
        self.post_renderers = []
        self.redraw()

    def on_press(self, widget, position):
        self.post_renderers = self.selected_renderers
        self.redraw()


# TODO: Consider renaming to DecoratedPanel?
class Window(UIWidget, containers.Overlay):

    DEFAULT_Z_ORDER = ZOrder.BASE

    def __init__(self, decorations, default_colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(default_colors=default_colors, **kwargs)
        self.frame = containers.Overlay()
        self.content = containers.Overlay()
        self.handlers = dict(
            on_key_press=on_key_press,
        )

        self.children.extend([
            toolkit.Decorated(
                decorations=decorations,
                decorated=self.content,
                align=Align.TOP_LEFT,
            ),
            self.frame,
        ])
        if title:
            self.frame.append(title)

    def append(self, widget):
        self.content.append(widget)

    def extend(self, widgets):
        self.content.extend(widgets)


class ModalWindow(Window, toolkit.Widget):

    DEFAULT_Z_ORDER = ZOrder.MODAL

    def __init__(self, align, padding, size, decorations, default_colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(
            align=align,
            padding=padding,
            decorations=decorations,
            default_colors=default_colors,
            title=title,
            on_key_press=on_key_press,
            **kwargs,
        )
        self.size = size

