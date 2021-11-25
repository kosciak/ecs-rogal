from ..geometry import Position, Vector, Size

from ..events import handlers

from ..console.core import Align, Padding

from .core import ZOrder
from . import core
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import states


class Widget:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.element = None
        self.manager = None

    def layout(self, manager, element, panel, z_order):
        self.manager = manager
        self.element = element
        manager.insert(
            element,
            ui_widget=self,
        )
        return super().layout(manager, element, panel, z_order)

    def redraw(self):
        if self.manager is None:
            return
        self.manager.redraw(self.element)


class Label(
        Widget,
        core.PostProcessed,
        basic.WithTextContent,
        decorations.WithClearedContent,
        decorations.WithPaddedContent,
        containers.Bin,
    ):

    def __init__(self, text, *, width=None, colors=None, align=None, padding=None):
        self.text = self._text(text, width=width, align=align)
        super().__init__(
            content=self.text,
            padding=padding,
            colors=colors,
        )


class FramedLabel(
        Widget,
        core.PostProcessed,
        basic.WithTextContent,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithPaddedContent,
        containers.Bin,
    ):

    def __init__(self, text, frame, *, width=None, colors=None, align=None, padding=None):
        self.text = self._text(text, width=width, align=align)
        super().__init__(
            content=self.text,
            frame=frame,
            align=align,
            colors=colors,
            padding=padding,
        )


# TODO: Use basic.WithTextContent
class TextInput(
        Widget,
        states.MouseOperated,
        containers.Stack,
    ):

    def __init__(self, ecs, width, *,
                 colors,
                 default_text=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            width=width,
            height=1,
            align=Align.TOP_LEFT,
            colors=colors,
        )
        self.text = basic.Text(
            default_text or '',
            width=width,
        )
        self.cursor = basic.Cursor(
            # colors=colors.invert(),
            blinking=1200,
        )
        self.cursor.position = Position(len(self.txt), 0)
        self.content.extend([
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

    def on_input(self, element, char):
        if len(self.txt) < self.width-1:
            before_cursor = self.txt[:self.cursor.position.x]
            after_cursor = self.txt[self.cursor.position.x:]
            self.txt = before_cursor + char + after_cursor
            self.cursor.move(Vector(1, 0))

    def on_edit(self, element, cmd):
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


# TODO: Consider: multiple Labels associated with each state, change content on state change?
class Button(
        Widget,
        states.Activable,
        states.MouseOperated,
        core.PostProcessed,
        decorations.WithPaddedContent,
        containers.Bin,
    ):

    def __init__(self, value, callback, content, *,
                 padding=None,
                 selected_colors=None, press_colors=None,
                 selected_renderers=None,
                ):
        self.button = content
        super().__init__(
            callback=callback, value=value,
            content=self.button,
            padding=padding, # NOTE: with padding whole area is mouse operated, including padding!
        )
        self.default_colors = self.button.colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])

    def enter(self):
        super().enter()
        self.button.colors = self.selected_colors
        self.button.post_renderers = self.selected_renderers
        self.redraw();

    def leave(self):
        super().leave()
        self.button.colors = self.default_colors
        self.button.post_renderers = []
        self.redraw()

    def press(self, position):
        super().press(position)
        self.button.colors = self.press_colors
        self.button.post_renderers = self.selected_renderers
        self.redraw()


class ButtonsRow(
        Widget,
        containers.WithContainedContent,
        decorations.WithPaddedContent,
        containers.Bin,
    ):
    def __init__(self, buttons=None, *, align=None, padding=None):
        container = containers.Row(
            buttons,
            align=align,
        )
        super().__init__(
            container=container,
            padding=padding,
        )


class ListItem(
        Widget,
        states.Activable,
        states.MouseOperated,
        states.WithHotkey,
        core.PostProcessed,
        containers.Row,
    ):

    def __init__(self, ecs, key_binding, callback, value, index, item, *,
                 colors,
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
            colors=colors,
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

    def on_mouse_over(self, element, position):
        for item in self.items:
            if item.is_focused and not item.is_hovered:
                return item.unfocus()

    def on_focus_change(self, element, direction):
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

    def on_select(self, element, value):
        for item in self.items:
            if item.is_focused or item.is_hovered:
                return item.toggle()

    def on_index(self, element, index):
        if index < len(self.items):
            self.items[index].toggle()


# TODO: Use decorations.With*Content and containers.Bin
# TODO: Consider renaming to FramedPanel?
class Window(Widget, containers.Stack):

    DEFAULT_Z_ORDER = ZOrder.BASE

    def __init__(self, frame, colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(**kwargs)
        self.outer = containers.Stack()
        # TODO: Instead of frame use header, footer?
        self.inner = containers.Stack()
        self.handlers.on_key_press.update(on_key_press or {})

        self.content.extend([
            decorations.Cleared(
                content=decorations.Framed(
                    content=self.inner,
                    frame=frame,
                    align=Align.TOP_LEFT,
                ),
                colors=colors,
            ),
            self.outer,
        ])
        if title:
            self.outer.append(title)

    def append(self, element):
        self.inner.append(element)

    def extend(self, widgets):
        self.inner.extend(widgets)


# TODO: Subclass Padded, or maybe some kind of WithPaddedContent?
class ModalWindow(Window, core.UIElement):

    DEFAULT_Z_ORDER = ZOrder.MODAL

    def __init__(self, size, align, frame, colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(
            width=size.width,
            height=size.height,
            align=align,
            frame=frame,
            colors=colors,
            title=title,
            on_key_press=on_key_press,
            **kwargs,
        )

