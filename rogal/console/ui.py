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

    def __init__(self, decorations, text, width, *,
                 on_mouse_click,
                 on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
                 align=Align.TOP_LEFT):
        text = toolkit.Text(text, align=Align.CENTER, width=width)
        super().__init__(decorations, text, align=align)
        self.on_mouse_click = on_mouse_click
        self.on_mouse_in = on_mouse_in
        self.on_mouse_over = on_mouse_over
        self.on_mouse_out = on_mouse_out

    def layout(self, manager, parent, panel, z_order=None):
        entity = super().layout(manager, parent, panel, z_order)
        manager.insert(entity, widget=self)
        manager.bind(
            entity,
            on_mouse_click=self.on_mouse_click,
            on_mouse_in=self.on_mouse_in,
            on_mouse_over=self.on_mouse_over,
            on_mouse_out=self.on_mouse_out,
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

    def layout(self, manager, parent, panel, z_order=None):
        z_order = z_order or toolkit.ZOrder.BASE
        entity = super().layout(manager, parent, panel, z_order)
        manager.insert(entity, widget=self)
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

    def layout(self, manager, parent, panel, z_order=None):
        position = toolkit.get_position(panel.root, self.size, self.align, self.padding)
        panel = panel.create_panel(position, self.size)
        z_order = z_order or toolkit.ZOrder.MODAL
        return super().layout(manager, parent, panel, z_order)


class WidgetsBuilder:

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
            text=text,
            width=self.button_width,
            on_mouse_click={
                handlers.MouseLeftButtonPress(self.ecs, value): callback,
            },
            # on_mouse_in={
            #     handlers.MouseIn(self.ecs): lambda *args: print(f'IN: {button.decorated.txt}'),
            # },
            # on_mouse_over={
            #     handlers.MouseIn(self.ecs): lambda *args: print(f'OVER: {button.decorated.txt}'),
            # },
            # on_mouse_out={
            #     handlers.MouseOut(self.ecs): lambda *args: print(f'OUT: {button.decorated.txt}'),
            # },
        )
        return button

    def create_buttons_row(self, callback, buttons):
        buttons_row = toolkit.Row(align=self.buttons_align)
        for text, value in buttons:
            buttons_row.append(self.create_button(text, callback, value))
        return buttons_row

    def create(self, widget_type, context):
        # TODO: Move layout definitions to data/ui.yaml ?
        if widget_type == 'YES_NO_PROMPT':
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

        if widget_type == 'IN_GAME':
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
        self.widgets_builder = WidgetsBuilder(self.ecs)

    def insert(self, entity, *,
               widget=None,
               panel=None,
               z_order=None,
               renderer=None,
              ):
        if widget:
            self.ecs.manage(components.UIWidget).insert(
                entity, widget, needs_update=False,
            )
        if panel:
            self.ecs.manage(components.ConsolePanel).insert(
                entity, panel, z_order or toolkit.ZOrder.BASE,
            )
        if renderer:
            self.ecs.manage(components.PanelRenderer).insert(
                entity, renderer,
            )

    def create(self, parent, *,
               panel=None,
               z_order=None,
               renderer=None,
              ):
        entity = self.ecs.create(
            components.ParentUIWidget(parent),
        )
        self.insert(entity, panel=panel, z_order=z_order, renderer=renderer)
        return entity

    def bind(self, entity, *,
             on_key_press=None,
             on_mouse_click=None,
             on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
            ):
        if on_key_press:
            self.ecs.manage(components.OnKeyPress).insert(
                entity, on_key_press,
            )
        if on_mouse_click:
            self.ecs.manage(components.OnMouseClick).insert(
                entity, on_mouse_click,
            )
        if on_mouse_in:
            self.ecs.manage(components.OnMouseIn).insert(
                entity, on_mouse_in,
            )
        if on_mouse_over:
            self.ecs.manage(components.OnMouseOver).insert(
                entity, on_mouse_over,
            )
        if on_mouse_out:
            self.ecs.manage(components.OnMouseOut).insert(
                entity, on_mouse_out,
            )

    def create_widget(self, widget_type, context):
        widget = self.widgets_builder.create(
            widget_type, context,
        )
        return widget

