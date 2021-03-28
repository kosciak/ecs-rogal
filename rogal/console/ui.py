import string

from .. import components

from ..geometry import Position, Vector, Size
from ..tiles import Colors

from ..events import handlers

from .. import render

from .core import Align, Padding
from . import toolkit


# TODO: frames overlapping, and fixing overlapped/overdrawn characters to merge borders/decorations
# TODO: Scrollable Panels?


class ZOrder:
    BASE = 1
    MODAL = 100


class UIWidget:

    def __init__(self, default_colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = toolkit.ClearPanel(
            colors=default_colors,
        )

    @property
    def colors(self):
        return self.renderer.colors

    @colors.setter
    def colors(self, colors):
        self.renderer.colors = colors

    def layout(self, manager, widget, panel, z_order=None):
        super().layout(manager, widget, panel, z_order)
        manager.insert(
            widget,
            ui_widget=self,
        )


class TextInput(UIWidget, toolkit.Container, toolkit.Widget):

    def __init__(self, ecs, width, *,
                 default_colors,
                 default_text=None,
                 align=Align.TOP_LEFT,
                 padding=Padding.ZERO,
                ):
        super().__init__(
            align=Align.TOP_LEFT,
            padding=padding,
            default_colors=default_colors,
        )
        self.size = Size(width, 1)
        self.text = toolkit.Text(
            default_text or '',
            width=width,
        )
        self.cursor = toolkit.Cursor(
            # colors=default_colors.invert(),
            blinking=1200,
        )
        self.cursor.position = Position(len(self.txt), 0)
        self.children.extend([
            self.text,
            # TODO: Show Cursor only if has focus and ready for input?
            self.cursor,
        ])
        self.handlers = dict(
            on_text_input={
                handlers.TextInput(): self.on_input,
            },
            on_key_press={
                handlers.TextEdit(ecs): self.on_edit,
            },
            # TODO: change cursor on mouse over
        )

    @property
    def txt(self):
        return self.text.txt

    @txt.setter
    def txt(self, txt):
        self.text.txt = txt

    def on_input(self, widget, char):
        if len(self.txt) < self.width-1:
            before_cursor = self.txt[:self.cursor.position.x]
            after_cursor = self.txt[self.cursor.position.x:]
            self.txt = before_cursor + char + after_cursor
            self.cursor.move(Vector(1, 0))

    def on_edit(self, widget, cmd):
        if not cmd:
            return
        elif cmd == 'CLEAR':
            self.txt = ''
            self.cursor.position = Position.ZERO
        elif cmd == 'BACKSPACE':
            before_cursor = self.txt[:self.cursor.position.x]
            if before_cursor:
                after_cursor = self.txt[self.cursor.position.x:]
                self.txt = before_cursor[:-1] + after_cursor
                self.cursor.move(Vector(-1, 0))
        elif cmd == 'DELETE':
            after_cursor = self.txt[self.cursor.position.x:]
            if after_cursor:
                before_cursor = self.txt[:self.cursor.position.x]
                self.txt = before_cursor + after_cursor[1:]
        elif cmd == 'HOME':
            self.cursor.position = Position.ZERO
        elif cmd == 'END':
            self.cursor.position = Position(len(self.txt), 0)
        elif cmd == 'FORWARD':
            if self.cursor.position.x < len(self.txt):
                self.cursor.move(Vector(1, 0))
        elif cmd == 'BACKWARD':
            if self.cursor.position.x > 0:
                self.cursor.move(Vector(-1, 0))
        elif cmd == 'PASTE':
            pass


class Button(UIWidget, toolkit.Decorated):

    def __init__(self, decorations, text, *,
                 on_mouse_click,
                 default_colors,
                 selected_colors=None, press_colors=None,
                 align=Align.TOP_LEFT,
                ):
        super().__init__(
            decorations=decorations,
            decorated=text,
            align=align,
            default_colors=default_colors,
        )
        self.default_colors = default_colors
        self.selected_colors = selected_colors or self.default_colors
        self.press_colors = press_colors or self.selected_colors
        self.handlers = dict(
            on_mouse_click=on_mouse_click,
            on_mouse_press={
                handlers.MouseLeftButton(): self.on_press,
            },
            on_mouse_up={
                handlers.MouseLeftButton(): self.on_select,
            },
            on_mouse_in={
                handlers.MouseIn(): lambda widget, *args: print(f'IN: {self.decorated.txt}'),
                handlers.MouseIn(): self.on_select,
            },
            on_mouse_over={
                handlers.MouseOver(): lambda widget, *args: print(f'OVER: {self.decorated.txt}'),
            },
            on_mouse_out={
                handlers.MouseOut(): lambda widget, *args: print(f'OUT: {self.decorated.txt}'),
                handlers.MouseOut(): self.on_unselect,
            },
        )

    @property
    def txt(self):
        return self.decorated.txt

    @txt.setter
    def txt(self, txt):
        self.decorated.txt = text

    def on_select(self, widget, value):
        self.colors = self.selected_colors

    def on_unselect(self, widget, value):
        self.colors = self.default_colors

    def on_press(self, widget, position):
        self.colors = self.press_colors


class Window(UIWidget, toolkit.Container):

    DEFAULT_Z_ORDER = ZOrder.BASE

    def __init__(self, decorations, default_colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(default_colors=default_colors, **kwargs)
        self.frame = toolkit.Container()
        self.content = toolkit.Container()
        self.handlers = dict(
            on_key_press=on_key_press,
        )

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


class ModalWindow(Window, toolkit.Widget):

    DEFAULT_Z_ORDER = ZOrder.MODAL

    def __init__(self, align, padding, size, decorations, default_colors, *,
                 title=None,
                 on_key_press=None,
                 **kwargs
                ):
        super().__init__(
            align=align,
            padding=padding,
            decorations=decorations,
            default_colors=default_colors,
            title=title,
            on_key_press=on_key_press,
            **kwargs,
        )
        self.size = size


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
                width=10,
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
            text=toolkit.Text(
                text,
                width=self.button_width,
                align=Align.CENTER,
            ),
            on_mouse_click={
                handlers.MouseLeftButton(value): callback,
            },
            default_colors=self.default_colors,
            selected_colors=self.default_colors.invert(),
            press_colors=Colors(
                fg=self.tileset.palette.bg,
                bg=self.tileset.palette.BRIGHT_WHITE
            ),
        )
        return button

    def create_buttons_row(self, callback, buttons, padding=Padding.ZERO):
        buttons_row = toolkit.Row(
            align=self.buttons_align,
            padding=padding,
        )
        for text, value in buttons:
            buttons_row.append(self.create_button(text, callback, value))
        return buttons_row

    def create_text_input(self, width, text=None, padding=Padding.ZERO):
        text_input = TextInput(
            self.ecs,
            width=width,
            default_text=text,
            padding=padding,
            # default_colors=self.default_colors,
            default_colors=Colors(fg=self.tileset.palette.fg, bg=self.tileset.palette.BRIGHT_BLACK),
        )
        return text_input

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
                    handlers.DiscardKeyPress(self.ecs): callback,
                },
            )

            msg = toolkit.Text(
                msg,
                align=Align.TOP_CENTER,
                padding=Padding(1, 0),
            )

            buttons = self.create_buttons_row(
                callback=callback,
                buttons=[
                    ['No',  False],
                    ['Yes', True],
                ],
                padding=Padding(1, 0, 0, 0),
            )

            # msg = self.create_text_input(38)

            widgets_layout.extend([msg, buttons])

        if widget_type == 'TEXT_INPUT_PROMPT':
            title = context['title']
            msg = context['msg']
            callback = context['callback']

            input_row = toolkit.Row(
                align=Align.TOP_CENTER,
                padding=Padding(1, 0),
            )
            prompt = toolkit.Text(
                "Text:",
            )
            text_input = self.create_text_input(
                width=26,
                padding=Padding(0, 0, 0, 1),
            )
            input_row.extend([prompt, text_input])

            buttons = self.create_buttons_row(
                callback=callback,
                buttons=[
                    ['Cancel', False],
                    ['OK',     text_input],
                ],
                padding=Padding(1, 0, 0, 0),
            )

            widgets_layout = self.create_modal_window(
                align=Align.TOP_CENTER,
                padding=Padding(12, 0),
                size=Size(40, 8),
                title=title,
                on_key_press={
                    handlers.OnKeyPress(self.ecs, 'common.SUBMIT', text_input): callback,
                    handlers.DiscardKeyPress(self.ecs): callback,
                },
            )

            widgets_layout.extend([input_row, buttons])

        if widget_type == 'ALPHABETIC_SELECT_PROMPT':
            title = context['title']
            msg = 'Select something'
            callback = context['callback']
            items = [f'index: {i}' for i in range(10)]

            msg = toolkit.Text(
                msg,
                align=Align.TOP_CENTER,
                padding=Padding(1, 0),
            )

            buttons = self.create_buttons_row(
                callback=callback,
                buttons=[
                    ['Cancel', False],
                ],
                padding=Padding(1, 0, 0, 0),
            )

            widgets_layout = self.create_modal_window(
                align=Align.TOP_CENTER,
                padding=Padding(12, 0),
                size=Size(
                    20,
                    self.window_decorations.height+msg.padded_height+buttons.padded_height+len(items)
                ),
                title=title,
                on_key_press={
                    handlers.AlphabeticIndexKeyPress(self.ecs, size=len(items)): callback,
                    handlers.DiscardKeyPress(self.ecs): callback,
                },
            )

            items_list = toolkit.List(
                align=Align.TOP_LEFT,
                padding=Padding(3, 0, 0, 0),
            )
            # TODO: Move to create_list()
            for i, item in enumerate(items):
                items_list.append(
                    # TODO: Move to create_list_item()
                    toolkit.Row(
                        widgets=[
                            toolkit.Text(
                                f'{string.ascii_lowercase[i]})',
                                padding=Padding(0, 1, 0, 0),
                            ),
                            toolkit.Text(
                                item,
                                colors=Colors(
                                    fg=self.tileset.palette.BLUE,
                                ),
                            ),
                        ],
                        align=Align.TOP_LEFT,
                        # TODO: on_mouse_click, on_mouse_hover
                    )
                )

            widgets_layout.extend([msg, items_list, buttons])

            return widgets_layout

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
        self.ecs.manage(components.InputFocus).insert(widget)

    def create_widget(self, widget_type, context):
        widget = self.widgets_builder.create(
            widget_type, context,
        )
        return widget

