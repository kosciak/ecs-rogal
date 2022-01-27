from ..events import EventType
from ..events import handlers

from . import containers
from . import decorations
from . import states
from . import widgets


class Window(
        states.Hoverable,
        widgets.Widget,
        decorations.WithContents,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.WithOverlayedContent,
        decorations.WithPostProcessedContent,
        decorations.Padded,
    ):

    def __init__(self, content, *,
                 title=None,
                 on_key_press=None,
                 **kwargs,
                ):
        super().__init__(
            content=content,
            **kwargs,
        )
        if title:
            self.title = title

        # TODO: Need to be moved somewhere else, just use signals?
        on_key_press = on_key_press or []
        for handler in on_key_press:
            self.bind(EventType.KEY_PRESS, handler)

    @property
    def title(self):
        return self.overlay.title

    @title.setter
    def title(self, title):
        self.overlay.title = title
        self.overlay.move_to_end('title', last=False)


class DialogWindow(
        states.Focusable,
        Window
    ):

    def __init__(self, content, *,
                 close_button=None,
                 response_key_handler=None,
                 **kwargs,
                ):
        self.buttons = widgets.ButtonsRow(
            selector='Dialog ButtonsRow',
        )
        content = containers.List(
            content=[
                content,
                self.buttons,
            ]
        )
        super().__init__(
            content=content,
            **kwargs,
        )
        if close_button:
            self.close_button = close_button
        self.bind(
            EventType.KEY_PRESS,
            handlers.DiscardKeyPress(self.on_close)
        )
        if response_key_handler:
            self.bind(
                EventType.KEY_PRESS,
                response_key_handler(self.on_response)
            )

    def close(self):
        self.emit('close')
        self.destroy()

    def response(self, value):
        self.emit('response', value)
        self.destroy()

    def on_close(self, source, value=None):
        self.close()

    def on_response(self, source, value):
        self.response(value)

    @property
    def close_button(self):
        return self.overlay.close_button

    @close_button.setter
    def close_button(self, close_button):
        self.overlay.close_button = close_button
        close_button.on('clicked', self.on_close)

    def add_button(self, button, value):
        self.buttons.append(button)
        button.on('clicked', self.on_response, value)

