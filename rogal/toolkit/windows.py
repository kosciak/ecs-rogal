from . import containers
from . import decorations
from . import states
from . import widgets


class Window(
        states.Hoverable,
        widgets.WithOverlay,
        widgets.FramedWidget,
    ):

    def __init__(self, content, frame=None, *,
                 align=None, width=None, height=None,
                 padding=None,
                 colors=None,
                 on_key_press=None,
                ):
        super().__init__(
            content=content, frame=frame,
            align=align, width=width, height=height,
            colors=colors,
            padding=padding,
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

