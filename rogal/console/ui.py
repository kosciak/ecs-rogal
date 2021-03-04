from enum import Enum

from .. import components

from ..geometry import Size
from ..tiles import Colors

from .. import render

from .core import Align, Padding, Panel
from .toolkit import get_position
from .toolkit import Decorations, Decorated, Text, Container, Row, Split



# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations
# TODO: Keep track of Z-order of Windows?
# TODO: Scrollable Panels?


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs

        self.wrapper = self.ecs.resources.wrapper
        self._root = None

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self.window_decorations = Decorations(
            *self.tileset.decorations['DSLINE'],
            colors=self.default_colors
        )

        self.title_decorations = Decorations(
            *self.tileset.decorations['MINIMAL_DSLINE'],
            colors=self.default_colors
        )
        self.title_align = Align.TOP_CENTER

        self.button_decorations = Decorations(
            *self.tileset.decorations['LINE'],
            colors=self.default_colors
        )
        self.buttons_align = Align.BOTTOM_CENTER

    @property
    def root(self):
        if self.ecs.resources.root_panel is None:
            self.ecs.resources.root_panel = self.wrapper.create_panel()
        self._root = self.ecs.resources.root_panel
        return self._root

    def create_window(self, window, window_type, context):
        if window_type == 'YES_NO_PROMPT':
            layout = YesNoPrompt(
                frame_decorations=self.window_decorations,
                title_decorations=self.title_decorations,
                title_align=self.title_align,
                button_decorations=self.button_decorations,
                buttons_align=self.buttons_align,
                **context
            )
        if window_type == 'IN_GAME':
            layout = InGame(
                self.ecs,
                frame_decorations=self.window_decorations,
                title_decorations=self.title_decorations,
                title_align=self.title_align,
            )

        for renderer in layout.layout(self.root):
            renderer = self.ecs.create(
                components.PanelRenderer(renderer),
                components.ParentWindow(window)
            )


class Window(Container):

    def __init__(self,
                 frame_decorations,
                 title=None, title_decorations=None, title_align=Align.TOP_LEFT):
        super().__init__()
        self.frame = Container()
        self.content = Container()

        self.widgets.extend([
            Decorated(
                decorations=frame_decorations,
                align=Align.TOP_LEFT,
                decorated=self.content,
            ),
            self.frame,
        ])
        if title:
            self.frame.append(
                Decorated(
                    decorations=title_decorations,
                    align=title_align, padding=Padding(0, 1),
                    decorated=Text(title, align=title_align),
                )
            )


class YesNoPrompt(Window):

    def __init__(self, title, msg,
                 frame_decorations,
                 title_decorations, title_align,
                 button_decorations, buttons_align):
        super().__init__(
            frame_decorations=frame_decorations,
            title=title,
            title_decorations=title_decorations,
            title_align=title_align,
        )
        self.align = Align.TOP_CENTER
        self.padding = Padding(12, 0)
        self.size = Size(40, 8)

        msg = Text(msg, align=Align.TOP_CENTER, padding=Padding(1, 0))

        buttons = Row(align=buttons_align)
        for button_msg in ['Yes', 'No']:
            buttons.append(
                Decorated(
                    decorations=button_decorations,
                    align=Align.TOP_LEFT,
                    decorated=Text(button_msg, align=Align.CENTER, width=8),
                )
            )

        self.content.extend([msg, buttons, ])

    def layout(self, panel):
        position = get_position(panel.root, self.size, self.align, self.padding)
        panel = panel.create_panel(position, self.size)
        yield from super().layout(panel)


class InGame:

    def __init__(self, ecs,
                 frame_decorations,
                 title_decorations, title_align):
        self.split = Split(bottom=12)

        camera = Window(
            frame_decorations=frame_decorations,
            title='mapcam',
            title_decorations=title_decorations,
            title_align=title_align,
        )
        camera.content.append(render.Camera(ecs))

        msg_log = Window(
            frame_decorations=frame_decorations,
            title='logs',
            title_decorations=title_decorations,
            title_align=title_align,
        )
        msg_log.content.append(render.MessageLog())

        self.split.extend([camera, msg_log])

    def layout(self, panel):
        yield from self.split.layout(panel)

