from . import containers
from . import decorations
from . import signals
from . import states
from . import widgets


class Window(
        widgets.Widget,
        signals.SignalsEmitter,
        states.Hoverable,
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
        # TODO: Need to be moved somewhere else
        self.events_handlers.on_key_press.extend(on_key_press or [])

