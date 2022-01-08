from . import containers
from . import decorations
from . import states
from . import widgets


class Window(
        widgets.Widget,
        states.Hoverable,
        containers.WithContainer,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.Padded,
    ):

    def __init__(self, content, frame, colors, *,
                 align=None,
                 padding=None,
                 on_key_press=None,):
        self.contents = content
        super().__init__(
            content=self.contents,
            align=align,
            frame=frame,
            colors=colors,
            padding=padding,
        )
        self._container = containers.Stack()

        # TODO: Need to be moved somewhere else, just use signals?
        self.events_handlers.on_key_press.extend(on_key_press or [])

    def layout_content(self, manager, parent, panel, z_order):
        # Layout padded, framed, cleared contents...
        z_order = super().layout_content(manager, parent, panel, z_order)
        # ... and all overlayed elements
        return self._container.layout_content(manager, parent, panel, z_order)

# TODO: WindowContent(Stack) with named attributes (OrderedDict?) And width/height from first layer?
#       window.attach('title', title)
#       window.attach('name', element)

