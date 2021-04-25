import string

from .. import components

from ..geometry import Size
from ..tiles import Colors

from ..events import handlers

from .. import render

from .core import Align, Padding, ZOrder
from . import basic
from . import containers
from . import decorations
from . import renderers
from . import widgets


# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations
# TODO: Scrollable Panels?


class WidgetsBuilder:

    def __init__(self, ecs):
        self.ecs = ecs

        self.tileset = self.ecs.resources.tileset
        self.default_colors = Colors(self.tileset.palette.fg, self.tileset.palette.bg)

        self.window_frame = decorations.Frame(
            *self.tileset.decorations.DSLINE,
            colors=None,
        )

        self.title_frame = decorations.Frame(
            *self.tileset.decorations.MINIMAL_DSLINE,
            colors=None,
        )
        self.title_align = Align.TOP_CENTER

        self.button_frame = decorations.Frame(
            *self.tileset.decorations.LINE,
            colors=None,
        )
        self.button_width = 8
        self.buttons_align = Align.BOTTOM_CENTER

    def create_window_title(self, title):
        if title is None:
            return
        title = decorations.Padded(
            content=decorations.Framed(
                content=basic.Text(
                    title,
                    colors=self.default_colors,
                    align=self.title_align,
                    # width=10,
                ),
                frame=self.title_frame,
                align=self.title_align,
            ),
            padding=Padding(0, 1),
        )
        return title

    def create_window(self, title=None, on_key_press=None):
        window = widgets.Window(
            frame=self.window_frame,
            default_colors=self.default_colors,
            title=self.create_window_title(title),
            on_key_press=on_key_press,
        )
        return window

    # def create_modal_window(self, align, padding, size, title=None, on_key_press=None):
    def create_modal_window(self, align, size, title=None, on_key_press=None):
        window = content=widgets.ModalWindow(
            # align=align, padding=padding,
            align=align,
            size=size,
            default_colors=self.default_colors,
            frame=self.window_frame,
            title=self.create_window_title(title),
            on_key_press=on_key_press,
        )
        return window

    def create_button(self, text, callback, value):
        button = widgets.Button(
            value, callback,
            default_colors=self.default_colors,
            text=basic.Text(
                text,
                width=self.button_width,
                align=Align.CENTER,
            ),
            frame=self.button_frame,
            # selected_colors=self.default_colors.invert(),
            press_colors=Colors(
                bg=self.tileset.palette.bg,
                fg=self.tileset.palette.BRIGHT_WHITE
            ),
            selected_renderers=[
                renderers.InvertColors(),
            ],
        )
        return button

    def create_buttons_row(self, callback, buttons, padding=Padding.ZERO):
        buttons_row = containers.Row(
            align=self.buttons_align,
            # padding=padding,
        )
        for text, value in buttons:
            buttons_row.append(self.create_button(text, callback, value))
        return buttons_row

    def create_text_input(self, width, text=None, padding=Padding.ZERO):
        text_input = widgets.TextInput(
            self.ecs,
            width=width,
            default_text=text,
            # padding=padding,
            # default_colors=self.default_colors,
            default_colors=Colors(fg=self.tileset.palette.fg, bg=self.tileset.palette.BRIGHT_BLACK),
        )
        return text_input

    def create_list_item(self, width, item, key_binding, callback, index):
        index_text = decorations.Padded(
            content=basic.Text(
                f'{key_binding})',
            ),
            padding=Padding(0, 1),
        )
        item_text = basic.Text(
            item,
            colors=Colors(
                fg=self.tileset.palette.BLUE,
            ),
            width=width-index_text.width,
        )

        list_item = widgets.ListItem(
            self.ecs,
            key_binding=key_binding,
            callback=callback, value=index,
            index=index_text, item=item_text,
            default_colors=self.default_colors,
            selected_renderers=[
                renderers.InvertColors(),
                renderers.PaintPanel(Colors(bg=item_text.colors.fg)),
            ],
        )

        return list_item

    def create_list_separator(self, width):
        separator = basic.Text(
            '-'*(width//3),
            width=width,
            # padding=Padding(0, 1),
            align=Align.TOP_CENTER,
        )

        return separator

    def create_yes_no_prompt(self, context):
        title = context['title']
        msg = context['msg']
        callback = context['callback']

        window = self.create_modal_window(
            align=Align.TOP_CENTER,
            size=Size(40, 8),
            title=title,
            on_key_press={
                handlers.YesNoKeyPress(self.ecs): callback,
                handlers.DiscardKeyPress(self.ecs): callback,
            },
        )

        msg = basic.Text(
            msg,
            align=Align.TOP_CENTER,
        )

        buttons = self.create_buttons_row(
            callback=callback,
            buttons=[
                ['No',  False],
                ['Yes', True],
            ],
        )

        window.extend([
            decorations.Padded(
                content=msg,
                padding=Padding(1, 0),
            ),
            decorations.Padded(
                content=buttons,
                padding=Padding(1, 0, 0, 0),
            ),
        ])

        widgets_layout = decorations.Padded(
            content=window,
            padding=Padding(12, 0),
        )
        return widgets_layout

    def create_text_input_prompt(self, context):
        title = context['title']
        msg = context['msg']
        callback = context['callback']

        prompt = basic.Text(
            "Text: ",
        )
        text_input = self.create_text_input(
            width=26,
        )

        input_row = containers.Row(
            align=Align.TOP_CENTER,
        )
        input_row.extend([
            prompt,
            text_input,
        ])

        buttons = self.create_buttons_row(
            callback=callback,
            buttons=[
                ['Cancel', False],
                ['OK',     text_input],
            ],
        )

        window = self.create_modal_window(
            align=Align.TOP_CENTER,
            size=Size(40, 8),
            title=title,
            on_key_press={
                handlers.OnKeyPress(self.ecs, 'common.SUBMIT', text_input): callback,
                handlers.DiscardKeyPress(self.ecs): callback,
            },
        )

        window.extend([
            decorations.Padded(
                content=input_row,
                padding=Padding(1, 0),
            ),
            decorations.Padded(
                content=buttons,
                padding=Padding(1, 0, 0, 0),
            ),
        ])

        widgets_layout = decorations.Padded(
            content=window,
            padding=Padding(12, 0),
        )
        return widgets_layout

    def create_alphabetic_select_prompt(self, context):
        title = context['title']
        msg = 'Select something'
        callback = context['callback']
        items = [f'index: {i}' for i in range(10)]

        msg = basic.Text(
            msg,
            align=Align.TOP_CENTER,
        )

        buttons = self.create_buttons_row(
            callback=callback,
            buttons=[
                ['Cancel', False],
            ],
        )

        window = self.create_modal_window(
            align=Align.TOP_CENTER,
            size=Size(
                20,
                self.window_frame.extents.height+msg.height+buttons.height+len(items)+4
            ),
            title=title,
            on_key_press={
                handlers.DiscardKeyPress(self.ecs): callback,
            },
        )

        items_list = widgets.ListBox(
            self.ecs,
            align=Align.TOP_LEFT,
        )
        # TODO: Move to create_list()
        for index, item in enumerate(items):
            if index == len(items) / 2:
                items_list.append_separator(
                    self.create_list_separator(18)
                )
            key_binding = string.ascii_lowercase[index]
            items_list.append_item(
                self.create_list_item(18, item, key_binding, callback, index)
            )

        window.extend([
            decorations.Padded(
                content=msg,
                padding=Padding(1, 0),
            ),
            decorations.Padded(
                content=items_list,
                padding=Padding(3, 0, 0, 0),
            ),
            decorations.Padded(
                content=buttons,
                padding=Padding(1, 0, 0, 0),
            ),
        ])

        widgets_layout = decorations.Padded(
            content=window,
            padding=Padding(8, 0),
        )
        return widgets_layout

    def create(self, widget_type, context):
        # TODO: Move layout definitions to data/ui.yaml ?
        if widget_type == 'YES_NO_PROMPT':
            widgets_layout = self.create_yes_no_prompt(context)

        if widget_type == 'TEXT_INPUT_PROMPT':
            widgets_layout = self.create_text_input_prompt(context)

        if widget_type == 'ALPHABETIC_SELECT_PROMPT':
            widgets_layout = self.create_alphabetic_select_prompt(context)

        if widget_type == 'IN_GAME':
            widgets_layout = containers.Split(bottom=12)

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

    def create(self, widget_type, context):
        widget = self.ecs.create(
            components.CreateUIWidget(
                widget_type=widget_type,
                context=context,
            ),
        )
        return widget

    def destroy(self, widget):
        self.ecs.manage(components.DestroyUIWidget).insert(widget)

    def create_child(self, parent):
        widget = self.ecs.create(
            components.ParentUIWidget(parent),
        )
        return widget

    def redraw(self, widget):
        self.ecs.manage(components.DestroyUIWidgetChildren).insert(widget)
        content = self.ecs.manage(components.UIWidget).get(widget)
        if content:
            content.invalidate()

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
            self.ecs.manage(components.Console).insert(
                widget, panel, z_order or ZOrder.BASE,
            )
        if renderer:
            self.ecs.manage(components.PanelRenderer).insert(
                widget, renderer,
            )

    def bind(self, widget, *,
             on_text_input=None,
             on_key_press=None,
             on_mouse_click=None, on_mouse_press=None, on_mouse_up=None,
             on_mouse_in=None, on_mouse_over=None, on_mouse_out=None,
             on_mouse_wheel=None,
            ):
        if on_text_input:
            self.ecs.manage(components.OnTextInput).insert(
                widget, on_text_input,
            )
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
        if on_mouse_wheel:
            self.ecs.manage(components.OnMouseWheel).insert(
                widget, on_mouse_wheel,
            )

    def grab_focus(self, widget):
        self.ecs.manage(components.GrabInputFocus).insert(widget)

    # TODO: get_focus -> just set current InputFocus value, not higher one!

    def release_focus(self, widget):
        self.ecs.manage(components.InputFocus).remove(widget)

    def create_widget(self, widget_type, context):
        widget = self.widgets_builder.create(
            widget_type, context,
        )
        return widget

