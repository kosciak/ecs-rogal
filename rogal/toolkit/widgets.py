from .core import ZOrder
from . import core
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import states
from . import signals


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
                 align=None, width=None, colors=None, padding=None):
        text = self._text(text, align=align, width=width)
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
                 align=None, width=None, colors=None, padding=None):
        self.label = self._text(label, align=align, width=width)
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
        signals.SignalsEmitter,
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
            padding=padding,
        )
        self.default_colors = self._button.colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.selected_renderers = list(selected_renderers or [])

    def enter(self):
        super().enter()
        self._button.colors = self.selected_colors
        self._button.post_renderers = self.selected_renderers
        # self.redraw();

    def leave(self):
        super().leave()
        self._button.colors = self.default_colors
        self._button.post_renderers = []
        # self.redraw()

    def press(self, position):
        super().press(position)
        self._button.colors = self.press_colors
        self._button.post_renderers = self.selected_renderers
        # self.redraw()

    def release(self, position):
        super().release(position)
        self._button.colors = self.selected_colors
        self._button.post_renderers = self.selected_renderers
        # self.redraw();

    def activate(self):
        self.emit('clicked')
        super().activate()


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
                 align=None, width=None, height=None, padding=None,
                 on_key_press=None,):
        self.contents = content
        # NOTE: Instead of using set_width / set_height we use 
        #       containers.Bin to force width and size of window's contents
        content = containers.Bin(
            content=self.contents,
            width=width,
            height=height,
        )
        super().__init__(
            content=content,
            align=align,
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
        self.handlers.on_key_press.extend(on_key_press or [])

