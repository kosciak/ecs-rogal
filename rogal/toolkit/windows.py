from ..collections.attrdict import OrderedAttrDict

from . import containers
from . import decorations
from . import states
from . import widgets


class Window(
        widgets.Widget,
        states.Hoverable,
        decorations.WithFramedContent,
        decorations.WithClearedContent,
        decorations.Padded,
    ):

    def __init__(self, content, frame, colors, *,
                 align=None, width=None, height=None,
                 padding=None,
                 on_key_press=None,):
        self.contents = content
        self.overlay = OrderedAttrDict()
        super().__init__(
            content=self.contents,
            align=align,
            width=width,
            height=height,
            frame=frame,
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

    def layout_content(self, manager, parent, panel, z_order):
        # Layout padded, framed, cleared contents...
        z_order = super().layout_content(manager, parent, panel, z_order)

        # ... and all overlayed elements
        for child in self.overlay.values():
            element = manager.create_child(parent)
            z_order = child.layout(manager, element, panel, z_order+1)
        return z_order

    def on_close(self, source, value):
        # NOTE: Handler for close button "click" signals, DiscardKeyPress events, etc
        self.destroy()

