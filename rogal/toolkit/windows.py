from . import containers
from . import decorations
from . import states
from . import widgets


class Window(
        states.Hoverable,
        widgets.FramedWidget,
        decorations.Overlayed,
    ):

    def __init__(self, content, *,
                 on_key_press=None,
                 **kwargs,
                ):
        super().__init__(
            content=content,
            **kwargs,
        )

        # TODO: Need to be moved somewhere else, just use signals?
        self.events_handlers.on_key_press.extend(on_key_press or [])

    @property
    def title(self):
        return self.overlay.title

    @title.setter
    def title(self, title):
        self.overlay.title = title
        self.overlay.move_to_end('title', last=False)

    def close(self):
        self.destroy()

    def on_close(self, source, value):
        # NOTE: Handler for close button "click" signals, DiscardKeyPress events, etc
        self.close()


class DialogWindow(Window):

    def add_button(self, button, value):
        self.buttons.append(button)
        button.on('clicked', self.on_button_clicked, value)

    def on_button_clicked(self, source, value):
        self.emit('response', value)
        self.close()

