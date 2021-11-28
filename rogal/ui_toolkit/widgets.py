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
        basic.WithTextContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, text, *,
                 width=None, colors=None, align=None, padding=None):
        text = self._text(text, width=width, align=align)
        super().__init__(
            content=text,
            padding=padding,
            colors=colors,
        )


class FramedLabel(
        Widget,
        basic.WithTextContent,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, label, frame, *,
                 width=None, colors=None, align=None, padding=None):
        self.label = self._text(label, width=width, align=align)
        super().__init__(
            content=self.label,
            frame=frame,
            align=align,
            colors=colors,
            padding=padding,
        )


# TODO: Consider: multiple Labels associated with each state, change content on state change?
class Button(
        Widget,
        states.Activable,
        states.MouseOperated,
        decorations.Padded,
    ):

    def __init__(self, value, callback, content, *,
                 padding=None,
                 selected_colors=None, press_colors=None,
                 selected_renderers=None,
                ):
        self._button = content
        super().__init__(
            callback=callback, value=value,
            content=self._button,
            padding=padding, # NOTE: with padding whole area is mouse operated, including padding!
        )
        self.default_colors = self._button.colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])

    def enter(self):
        super().enter()
        self._button.colors = self.selected_colors
        self._button.post_renderers = self.selected_renderers
        self.redraw();

    def leave(self):
        super().leave()
        self._button.colors = self.default_colors
        self._button.post_renderers = []
        self.redraw()

    def press(self, position):
        super().press(position)
        self._button.colors = self.press_colors
        self._button.post_renderers = self.selected_renderers
        self.redraw()


class ButtonsRow(
        Widget,
        containers.WithContainer,
        decorations.Padded,
    ):
    def __init__(self, buttons=None, *,
                 align=None, padding=None):
        self._container = containers.Row(
            content=buttons,
            align=align,
        )
        super().__init__(
            content=self._container,
            padding=padding,
        )


class Window(
        Widget,
        containers.WithContainer,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.Padded,
    ):

    def __init__(self, content, frame, colors, *,
                 width=None, height=None, align=None, padding=None,
                 on_key_press=None,):
        self.contents = content
        # NOTE: Instead of using set_width / set_height we use 
        #       containers.Bin to force width and size of window's contents
        content = containers.Bin(
            content=self.contents,
            width=width,
            height=height,
            align=align,
        )
        super().__init__(
            content=content,
            frame=frame,
            colors=colors,
            padding=padding,
        )
        # Replace Cleared(Framed(content)) with Stack
        self._container = containers.Stack(
            content=self.content,
            width=self.content.width,
            height=self.content.height,
        )
        self.content = self._container
        self.handlers.on_key_press.update(on_key_press or {})


# TODO: Needs major rewrite
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


# TODO: Needs major rewrite
class ListItem(
        Widget,
        states.Activable,
        states.MouseOperated,
        states.WithHotkey,
        # core.PostProcessed,
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
        # self.post_renderers = self.selected_renderers
        self.redraw();

    def leave(self):
        super().leave()
        self.post_renderers = []
        self.redraw()

    def press(self, position):
        super().press(position)
        # self.post_renderers = self.selected_renderers
        self.redraw()

    def focus(self):
        super().focus()
        # self.post_renderers = self.selected_renderers
        self.redraw()

    def unfocus(self):
        super().unfocus()
        # self.post_renderers = []
        self.redraw()


# TODO: Needs major rewrite
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

