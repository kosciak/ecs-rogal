from enum import Enum, auto

from ..geometry import Position, Vector, Size

from ..events import handlers

from .core import Align, ZOrder
from . import toolkit
from . import basic
from . import containers
from . import decorations
from . import renderers


class UIWidget:

    def __init__(self, default_colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = renderers.ClearPanel(
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


class WidgetState(Enum):
    HOVERED = auto()
    PRESSED = auto()
    FOCUSED = auto()
    SELECTED = auto()


class Stateful:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = set()

    @property
    def is_hovered(self):
        return WidgetState.HOVERED in self.states

    @property
    def is_pressed(self):
        return WidgetState.PRESSD in self.states

    @property
    def is_focused(self):
        return WidgetState.FOCUSED in self.states

    @property
    def is_selected(self):
        return WidgetState.SELECTED in self.states

    def enter(self):
        self.states.add(WidgetState.HOVERED)

    def leave(self):
        self.states.discard(WidgetState.HOVERED)
        self.states.discard(WidgetState.PRESSED)

    def press(self, position):
        self.states.add(WidgetState.PRESSED)

    def focus(self):
        self.states.add(WidgetState.FOCUSED)

    def unfocus(self):
        self.states.discard(WidgetState.FOCUSED)

    def select(self):
        self.states.add(WidgetState.SELECTED)

    def unselect(self):
        self.states.discard(WidgetState.SELECTED)

    def toggle(self):
        is_selected = WidgetState.SELECTED in self.states
        if is_selected:
            self.unselect()
        else:
            self.select()


class MouseOperated(Stateful):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers.on_mouse_click.update({
            handlers.MouseLeftButton(): self.on_click,
        })
        self.handlers.on_mouse_press.update({
            handlers.MouseLeftButton(): self.on_press,
        })
        self.handlers.on_mouse_up.update({
            handlers.MouseLeftButton(): self.on_enter,
        })
        self.handlers.on_mouse_in.update({
            handlers.MouseIn(): self.on_enter,
        })
        self.handlers.on_mouse_over.update({
            handlers.MouseOver(): self.on_over,
        })
        self.handlers.on_mouse_out.update({
            handlers.MouseOut(): self.on_leave,
        })

    def on_enter(self, widget, *args, **kwargs):
        self.enter()

    def on_over(self, widget, position, *args, **kwargs):
        self.hover(position)

    def on_leave(self, widget, *args, **kwargs):
        self.leave()

    def on_press(self, widget, position, *args, **kwargs):
        self.press(position)

    def on_click(self, widget, position, *args, **kwargs):
        self.toggle()

    def hover(self, position):
        if not self.is_hovered:
            self.enter()


class WithHotkey(Stateful):

    def __init__(self, ecs, key_binding, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers.on_key_press.update({
            handlers.OnKeyPress(ecs, key_binding): self.on_hotkey,
        })

    def on_hotkey(self, widget, key, *args, **kwargs):
        self.toggle()


class Activable:

    def __init__(self, callback, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.value = value

    def activate(self):
        return self.callback(self.widget, self.value)

    def select(self):
        super().select()
        self.activate()


class TextInput(MouseOperated, UIWidget, containers.Stack, toolkit.Widget):

    def __init__(self, ecs, width, *,
                 default_colors,
                 default_text=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            width=width,
            height=1,
            align=Align.TOP_LEFT,
            default_colors=default_colors,
        )
        self.text = basic.Text(
            default_text or '',
            width=width,
        )
        self.cursor = basic.Cursor(
            # colors=default_colors.invert(),
            blinking=1200,
        )
        self.cursor.position = Position(len(self.txt), 0)
        self.children.extend([
            self.text,
            # TODO: Show Cursor only if has focus and ready for input?
            self.cursor,
        ])
        self.handlers.on_text_input.update({
            handlers.TextInput(): self.on_input,
        })
        self.handlers.on_key_press.update({
            handlers.TextEdit(ecs): self.on_edit,
        })

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


class Button(Activable, MouseOperated, UIWidget, toolkit.PostProcessed, decorations.Framed):

    def __init__(self, value, callback, text, frame, *,
                 default_colors,
                 selected_colors=None, press_colors=None,
                 selected_renderers=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            callback=callback, value=value,
            content=text,
            frame=frame,
            align=align,
            default_colors=default_colors,
        )
        self.default_colors = default_colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])

    @property
    def txt(self):
        return self.content.txt

    @txt.setter
    def txt(self, txt):
        self.content.txt = text

    def enter(self):
        super().enter()
        self.colors = self.selected_colors
        self.post_renderers = self.selected_renderers
        self.redraw();

    def leave(self):
        super().leave()
        self.colors = self.default_colors
        self.post_renderers = []
        self.redraw()

    def press(self, position):
        super().press(position)
        self.colors = self.press_colors
        self.post_renderers = self.selected_renderers
        self.redraw()


class ListItem(Activable, MouseOperated, WithHotkey, UIWidget, toolkit.PostProcessed, containers.Row):

    def __init__(self, ecs, key_binding, callback, value, index, item, *,
                 default_colors,
                 selected_renderers=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            ecs=ecs, key_binding=key_binding,
            callback=callback, value=value,
            content=[
                index,
                item,
            ],
            align=align,
            default_colors=default_colors,
        )
        self.selected_renderers = list(selected_renderers or [])

    def enter(self):
        super().enter()
        self.post_renderers = self.selected_renderers
        self.redraw();

    def leave(self):
        super().leave()
        self.post_renderers = []
        self.redraw()

    def press(self, position):
        super().press(position)
        self.post_renderers = self.selected_renderers
        self.redraw()

    def focus(self):
        super().focus()
        self.post_renderers = self.selected_renderers
        self.redraw()

    def unfocus(self):
        super().unfocus()
        self.post_renderers = []
        self.redraw()


class ListBox(containers.List):

    def __init__(self, ecs, align=Align.TOP_LEFT):
        super().__init__(align=align)
        self.items = []
        self.handlers.on_key_press.update({
            handlers.NextPrevKeyPress(ecs, 'list.NEXT', 'list.PREV'): self.on_focus_change,
            handlers.OnKeyPress(ecs, 'list.SELECT'): self.on_select,
        })
        self.handlers.on_mouse_over.update({
            handlers.MouseOver(): self.on_mouse_over,
        })

    def append_item(self, item):
        self.append(item)
        self.items.append(item)

    def append_separator(self, separator):
        self.append(separator)

    def on_mouse_over(self, widget, position):
        for item in self.items:
            if item.is_focused and not item.is_hovered:
                return item.unfocus()

    def on_focus_change(self, widget, direction):
        index = None
        for i, item in enumerate(self.items):
            if item.is_focused or item.is_hovered:
                index = i
                break
        if index is not None:
            self.items[index].unfocus()
            self.items[index].leave()
            index += direction
            index %= len(self.items)
            self.items[index].focus()
        else:
            index = max(direction-1, -1)
            self.items[index].focus()

    def on_select(self, widget, value):
        for item in self.items:
            if item.is_focused or item.is_hovered:
                return item.toggle()

    def on_index(self, widget, index):
        if index < len(self.items):
            self.items[index].toggle()



# TODO: Consider renaming to FramedPanel?
class Window(UIWidget, containers.Stack):

    DEFAULT_Z_ORDER = ZOrder.BASE

    def __init__(self, frame, default_colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(default_colors=default_colors, **kwargs)
        self.frame = containers.Stack()
        # TODO: Instead of frame use header, footer?
        self.content = containers.Stack()
        self.handlers.on_key_press.update(on_key_press or {})

        self.children.extend([
            decorations.Framed(
                content=self.content,
                frame=frame,
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

    def __init__(self, size, align, frame, default_colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(
            width=size.width,
            height=size.height,
            align=align,
            frame=frame,
            default_colors=default_colors,
            title=title,
            on_key_press=on_key_press,
            **kwargs,
        )

