from .. import components

from ..geometry import Size
from ..tiles import Colors

from ..events import handlers

from .. import render

from .core import Align, Padding
from . import toolkit


# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations
# TODO: Scrollable Panels?
# TODO: TextInput
# TODO: Cursor (blinking)


class WindowTitle(toolkit.Decorated):

    def __init__(self, decorations, text, align=Align.TOP_LEFT):
        text = toolkit.Text(text, align=align)
        super().__init__(decorations, text, align=align, padding=Padding(0, 1))


class Button(toolkit.Decorated):

    def __init__(self, decorations, width, text, on_mouse_click, align=Align.TOP_LEFT):
        text = toolkit.Text(text, align=Align.CENTER, width=width)
        super().__init__(decorations, text, align=align)
        self.on_mouse_click = on_mouse_click

    def layout(self, manager, parent, panel, z_order=toolkit.ZOrder.BASE):
        entity = super().layout(manager, parent, panel, z_order)
        manager.bind(
            entity,
            on_mouse_click=self.on_mouse_click,
        )
        return entity


class Window(toolkit.Container):

    def __init__(self, decorations, title=None, on_key_press=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = toolkit.Container()
        self.content = toolkit.Container()
        self.on_key_press = on_key_press

        self.widgets.extend([
            toolkit.Decorated(
                decorations=decorations,
                align=Align.TOP_LEFT,
                decorated=self.content,
            ),
            self.frame,
        ])
        if title:
            self.frame.append(title)

    def append(self, widget):
        self.content.append(widget)

    def extend(self, widgets):
        self.content.extend(widgets)

    def layout(self, manager, parent, panel, z_order=toolkit.ZOrder.BASE):
        entity = super().layout(manager, parent, panel, z_order)
        manager.bind(
            entity,
            on_key_press=self.on_key_press,
        )
        return entity


class ModalWindow(Window, toolkit.Widget):

    def __init__(self, align, padding, size, decorations, title=None, on_key_press=None, *args, **kwargs):
        super().__init__(
            align=align,
            padding=padding,
            decorations=decorations,
            title=title,
            on_key_press=on_key_press,
            *args, **kwargs,
        )
        self.size = size

    def layout(self, manager, parent, panel, z_order=toolkit.ZOrder.MODAL):
        position = toolkit.get_position(panel.root, self.size, self.align, self.padding)
        panel = panel.create_panel(position, self.size)
        return super().layout(manager, parent, panel, z_order)


class WidgetsLayoutManager:

    def __init__(self, ecs):
        self.ecs = ecs

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self.window_decorations = toolkit.Decorations(
            *self.tileset.decorations['DSLINE'],
            colors=self.default_colors
        )

        self.title_decorations = toolkit.Decorations(
            *self.tileset.decorations['MINIMAL_DSLINE'],
            colors=self.default_colors
        )
        self.title_align = Align.TOP_CENTER

        self.button_decorations = toolkit.Decorations(
            *self.tileset.decorations['LINE'],
            colors=self.default_colors
        )
        self.button_width = 8
        self.buttons_align = Align.BOTTOM_CENTER

    def create_title(self, title):
        if title is None:
            return
        title = WindowTitle(
            decorations=self.title_decorations,
            text=title,
            align=self.title_align,
        )
        return title

    def create_window(self, title=None, on_key_press=None):
        window = Window(
            decorations=self.window_decorations,
            title=self.create_title(title),
            on_key_press=on_key_press,
        )
        return window

    def create_modal_window(self, align, padding, size, title=None, on_key_press=None):
        window = ModalWindow(
            align=align, padding=padding, size=size,
            decorations=self.window_decorations,
            title=self.create_title(title),
            on_key_press=on_key_press,
        )
        return window

    def create_button(self, text, callback, value):
        button = Button(
            decorations=self.button_decorations,
            width=self.button_width,
            text=text,
            on_mouse_click={
                handlers.MouseLeftButtonPress(self.ecs, value): callback,
            },
        )
        return button

    def create_buttons_row(self, callback, buttons):
        buttons_row = toolkit.Row(align=self.buttons_align)
        for text, value in buttons:
            buttons_row.append(self.create_button(text, callback, value))
        return buttons_row

    def create(self, window, window_type, context):
        # TODO: Move layout definitions to data/ui.yaml ?
        if window_type == 'YES_NO_PROMPT':
            title = context['title']
            msg = context['msg']
            callback = context['callback']

            widgets_layout = self.create_modal_window(
                align=Align.TOP_CENTER,
                padding=Padding(12, 0),
                size=Size(40, 8),
                title=title,
                on_key_press={
                    handlers.YesNoKeyPress(self.ecs): callback,
                },
            )

            msg = toolkit.Text(msg, align=Align.TOP_CENTER, padding=Padding(1, 0))
            buttons = self.create_buttons_row(
                callback=callback,
                buttons=[
                    ['Yes', True],
                    ['No',  False],
                ],
            )

            widgets_layout.extend([msg, buttons])

        if window_type == 'IN_GAME':
            widgets_layout = toolkit.Split(bottom=12)

            camera = self.create_window(title='mapcam')
            camera.content.append(render.Camera(self.ecs))

            msg_log = self.create_window(title='logs')
            msg_log.content.append(render.MessageLog())

            widgets_layout.extend([camera, msg_log])

        return widgets_layout


class UIManager:

    def __init__(self, ecs):
        self.ecs = ecs
        self.layout_manager = WidgetsLayoutManager(self.ecs)

    def create(self, parent, *,
               panel=None,
               renderer=None,
               z_order=None,
              ):
        entity = self.ecs.create(
            components.ParentWindow(parent),
            panel and components.ConsolePanel(panel),
            renderer and components.PanelRenderer(renderer),
            z_order and components.ZOrder(z_order),
        )
        return entity

    def bind(self, entity, on_key_press=None, on_mouse_click=None, on_mouse_over=None):
        if on_key_press:
            self.ecs.manage(components.OnKeyPress).insert(
                entity, on_key_press,
            )
        if on_mouse_click:
            self.ecs.manage(components.OnMouseClick).insert(
                entity, on_mouse_click,
            )
        if on_mouse_over:
            self.ecs.manage(components.OnMouseOver).insert(
                entity, on_mouse_over,
            )

    def create_widgets_layout(self, window, window_type, context):
        widgets_layout = self.layout_manager.create(
            window, window_type, context,
        )
        return widgets_layout

