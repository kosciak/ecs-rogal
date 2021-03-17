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


class Button(toolkit.Decorated):

    def __init__(self, decorations, text, width, *,
                 default_colors,
                 on_mouse_click, on_mouse_press=None, on_mouse_up=None,
                 on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
                 selected_colors=None, press_colors=None,
                 align=Align.TOP_LEFT,
                ):
        text = toolkit.Text(text, align=Align.CENTER, width=width)
        super().__init__(decorations, text, align=align)
        self.default_colors = default_colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.renderer = toolkit.ClearPanel(self.default_colors)
        self.on_mouse_click = on_mouse_click
        self.on_mouse_press = on_mouse_press
        self.on_mouse_up = on_mouse_up
        self.on_mouse_in = on_mouse_in
        self.on_mouse_over = on_mouse_over
        self.on_mouse_out = on_mouse_out

    def set_colors(self, colors):
        self.renderer.colors = colors

    def layout(self, manager, widget, panel, z_order=None):
        super().layout(manager, widget, panel, z_order)
        manager.insert(
            widget,
            ui_widget=self,
            renderer=self.renderer,
        )
        manager.bind(
            widget,
            on_mouse_click=self.on_mouse_click,
            on_mouse_press=self.on_mouse_press,
            on_mouse_up=self.on_mouse_up,
            on_mouse_in=self.on_mouse_in,
            on_mouse_over=self.on_mouse_over,
            on_mouse_out=self.on_mouse_out,
        )


class Window(toolkit.Container):

    def __init__(self, decorations, default_colors,
                 title=None,
                 on_key_press=None,
                 *args, **kwargs
                ):
        super().__init__(*args, **kwargs)
        self.frame = toolkit.Container()
        self.content = toolkit.Container()
        self.default_colors=default_colors
        self.on_key_press = on_key_press

        self.children.extend([
            toolkit.Decorated(
                decorations=decorations,
                decorated=self.content,
                align=Align.TOP_LEFT,
            ),
            self.frame,
        ])
        if title:
            self.frame.append(title)

    def append(self, widget):
        self.content.append(widget)

    def extend(self, widgets):
        self.content.extend(widgets)

    def layout(self, manager, widget, panel, z_order=None):
        z_order = z_order or toolkit.ZOrder.BASE
        super().layout(manager, widget, panel, z_order)
        manager.insert(
            widget,
            ui_widget=self,
            renderer=toolkit.ClearPanel(self.default_colors),
        )
        manager.bind(
            widget,
            on_key_press=self.on_key_press,
        )


class ModalWindow(Window, toolkit.Widget):

    def __init__(self, align, padding, size, decorations, default_colors,
                 title=None,
                 on_key_press=None,
                 *args, **kwargs
                ):
        super().__init__(
            align=align,
            padding=padding,
            decorations=decorations,
            default_colors=default_colors,
            title=title,
            on_key_press=on_key_press,
            *args, **kwargs,
        )
        self.size = size

    def layout(self, manager, widget, panel, z_order=None):
        z_order = z_order or toolkit.ZOrder.MODAL
        super().layout(manager, widget, panel, z_order)


class WidgetsBuilder:

    def __init__(self, ecs):
        self.ecs = ecs

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self.window_decorations = toolkit.Decorations(
            *self.tileset.decorations.DSLINE,
            colors=None,
        )

        self.title_decorations = toolkit.Decorations(
            *self.tileset.decorations.MINIMAL_DSLINE,
            colors=None,
        )
        self.title_align = Align.TOP_CENTER

        self.button_decorations = toolkit.Decorations(
            *self.tileset.decorations.LINE,
            colors=None,
        )
        self.button_width = 8
        self.buttons_align = Align.BOTTOM_CENTER

    def create_window_title(self, title):
        if title is None:
            return
        title = toolkit.Decorated(
            decorations=self.title_decorations,
            decorated=toolkit.Text(
                title,
                colors=self.default_colors,
                align=self.title_align,
            ),
            align=self.title_align,
            padding=Padding(0, 1),
        )
        return title

    def create_window(self, title=None, on_key_press=None):
        window = Window(
            decorations=self.window_decorations,
            default_colors=self.default_colors,
            title=self.create_window_title(title),
            on_key_press=on_key_press,
        )
        return window

    def create_modal_window(self, align, padding, size, title=None, on_key_press=None):
        window = ModalWindow(
            align=align, padding=padding, size=size,
            default_colors=self.default_colors,
            decorations=self.window_decorations,
            title=self.create_window_title(title),
            on_key_press=on_key_press,
        )
        return window

    def create_button(self, text, callback, value):
        button = Button(
            decorations=self.button_decorations,
            text=text,
            width=self.button_width,
            default_colors=self.default_colors,
            selected_colors=self.default_colors.invert(),
            press_colors=Colors(fg=self.tileset.palette.bg, bg=self.tileset.palette.BRIGHT_WHITE),
            on_mouse_click={
                handlers.MouseLeftButton(self.ecs, value): callback,
            },
            on_mouse_press={
                handlers.MouseLeftButton(self.ecs): lambda widget, *args: button.set_colors(button.press_colors),
            },
            on_mouse_up={
                handlers.MouseLeftButton(self.ecs): lambda widget, *args: button.set_colors(button.selected_colors),
            },
            # TODO: Clean up this mess of handlers!
            on_mouse_in={
                handlers.MouseIn(self.ecs): lambda widget, *args: print(f'IN: {button.decorated.txt}'),
                handlers.MouseIn(self.ecs): lambda widget, *args: button.set_colors(button.selected_colors),
            },
            on_mouse_over={
                handlers.MouseOver(self.ecs): lambda widget, *args: print(f'OVER: {button.decorated.txt}'),
            },
            on_mouse_out={
                handlers.MouseOut(self.ecs): lambda widget, *args: print(f'OUT: {button.decorated.txt}'),
                handlers.MouseOut(self.ecs): lambda widget, *args: button.set_colors(button.default_colors),
            },
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

    def insert(self, widget, *,
               ui_widget=None,
               panel=None,
               z_order=None,
               renderer=None,
              ):
        if ui_widget:
            self.ecs.manage(components.UIWidget).insert(
                widget, ui_widget, needs_update=False,
            )
        if panel:
            self.ecs.manage(components.ConsolePanel).insert(
                widget, panel, z_order or toolkit.ZOrder.BASE,
            )
        if renderer:
            self.ecs.manage(components.PanelRenderer).insert(
                widget, renderer,
            )

    def create(self, parent, panel=None, z_order=None, *,
               renderer=None,
              ):
        widget = self.ecs.create(
            components.ParentUIWidget(parent),
        )
        self.insert(widget, panel=panel, z_order=z_order, renderer=renderer)
        return widget

    def bind(self, widget, *,
             on_key_press=None,
             on_mouse_click=None, on_mouse_press=None, on_mouse_up=None,
             on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
            ):
        if on_key_press:
            self.ecs.manage(components.OnKeyPress).insert(
                widget, on_key_press,
            )
        if on_mouse_click:
            self.ecs.manage(components.OnMouseClick).insert(
                widget, on_mouse_click,
            )
        if on_mouse_press:
            self.ecs.manage(components.OnMousePress).insert(
                widget, on_mouse_press,
            )
        if on_mouse_up:
            self.ecs.manage(components.OnMouseUp).insert(
                widget, on_mouse_up,
            )
        if on_mouse_in:
            self.ecs.manage(components.OnMouseIn).insert(
                widget, on_mouse_in,
            )
        if on_mouse_over:
            self.ecs.manage(components.OnMouseOver).insert(
                widget, on_mouse_over,
            )
        if on_mouse_out:
            self.ecs.manage(components.OnMouseOut).insert(
                widget, on_mouse_out,
            )

    def create_widget(self, widget_type, context):
        widget = self.widgets_builder.create(
            widget_type, context,
        )
        return widget

