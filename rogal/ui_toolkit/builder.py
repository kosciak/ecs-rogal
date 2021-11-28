import string

from ..data import Decorations, ProgressBars, Spinners
from ..data import data_store
from ..geometry import Size

from ..events import handlers

from .. import render

from ..console.core import Align, Padding, Colors

from . import basic
from . import containers
from . import decorations
from . import renderers
from . import widgets


# TODO: Scrollable Panels?


class WidgetsBuilder:

    def __init__(self, ecs):
        self.ecs = ecs

        self.styles = data_store.ui_style

        self.default_colors = Colors("fg", "bg")

    def get_style(self, selectors):
        style = {}
        for selector in selectors.split(','):
            style.update(
                self.styles.get(selector.strip())
            )
        return style

    def create(self, element_cls, style, *args, **kwargs):
        if isinstance(style, str):
            style = self.get_style(style)
        element = element_cls(
            *args,
            **kwargs,
            **style,
        )
        return element

    def create_framed_label(self, style, txt):
        if txt is None:
            return

        label = self.create(
            widgets.Label, style.pop('label', {}),
            txt,
        )
        frame = self.create(
            basic.Frame, style.pop('frame', {}),
        )
        framed_label = self.create(
            widgets.FramedLabel, style,
            label=label,
            frame=frame,
        )

        return framed_label

    def create_window(self, style, content, title=None, on_key_press=None):
        frame = self.create(
            basic.Frame, style.pop('frame', {}),
        )
        title = self.create_framed_label(
            self.get_style('.title'),
            txt=title,
        )
        window = self.create(
            widgets.Window, style,
            content=content,
            frame=frame,
            on_key_press=on_key_press,
        )
        window.append(title)
        return window

    def create_modal_window(self, style, content, width=None, height=None, title=None, on_key_press=None):
        frame = self.create(
            basic.Frame, style.pop('frame', {}),
        )
        title = self.create_framed_label(
            self.get_style('.title'),
            txt=title,
        )
        window = self.create(
            widgets.Window, style,
            content=content,
            # content=containers.Stack(),
            width=width,
            height=height,
            frame=frame,
            on_key_press=on_key_press,
        )
        window.default_z_order=500
        window.append(title)
        return window

    def create_button(self, style, content, callback, value):
        button = self.create(
            widgets.Button, style,
            value, callback,
            content=content,
            # selected_colors=self.default_colors.invert(),
            press_colors=Colors(
                bg="bg",
                fg="BRIGHT_WHITE"
            ),
            selected_renderers=[
                renderers.InvertColors(),
            ],
        )
        return button

    def create_buttons_row(self, style, callback, buttons):
        buttons_row = self.create(
            widgets.ButtonsRow, style,
        )
        for text, value in buttons:
            content = self.create_framed_label(
                self.get_style('.button'),
                text,
            )
            button = self.create_button(
                self.get_style('Button'),
                content,
                callback, value,
            )
            buttons_row.append(button)
        return buttons_row

    def create_text_input(self, width, text=None):
        text_input = self.create(
            widgets.TextInput, 'TextInput',
            self.ecs,
            width=width,
            default_text=text,
        )
        return text_input

    def create_list_item(self, item, key_binding, callback, index):
        index_text = decorations.Padded(
            content=basic.Text(
                f'{key_binding})',
            ),
            padding=Padding(0, 1),
        )
        item_text = basic.Text(
            item,
            colors=Colors(
                fg="BLUE",
            ),
            width=0,
        )

        list_item = widgets.ListItem(
            self.ecs,
            key_binding=key_binding,
            callback=callback, value=index,
            index=index_text, item=item_text,
            colors=self.default_colors,
            selected_renderers=[
                renderers.InvertColors(),
                renderers.PaintPanel(Colors(bg=item_text.colors.fg)),
            ],
        )

        return list_item

    def create_list_separator(self):
        separator = decorations.Padded(
            content=basic.HorizontalSeparator(
                [0x2500, 0x251c, 0x2524, ],
            ),
            padding=Padding(0, -1),
        )

        # separator = basic.HorizontalSeparator(
        #     '-><',
        #     width=10,
        #     align=Align.CENTER,
        # )

        return separator

    def create_yes_no_prompt(self, context):
        title = context['title']
        msg = context['msg']
        callback = context['callback']

        msg = self.create(
            widgets.Label, 'Dialog Label',
            msg,
        )

        buttons_row = self.create_buttons_row(
            self.get_style('ButtonsRow'),
            callback=callback,
            buttons=[
                ['No',  False],
                ['Yes', True],
            ],
        )

        progress_bar = self.create(
            basic.ProgressBarAnimatedDemo, 'ProgressBar',
            value=.75,
            width=24,
            # height=3,
            frame_duration=150,
        )

        spinner = self.create(
            basic.Spinner, 'Spinner',
        )

        content = containers.List([
            # progress_bar,
            # spinner,
            msg,
            buttons_row,
        ], align=Align.TOP)

        # content = containers.Stack([
        #     # progress_bar,
        #     # spinner,
        #     msg,
        #     buttons_row,
        # ])

        window = self.create_modal_window(
            self.get_style('Window, Window.modal'),
            content=content,
            width=40,
            # height=6,
            title=title,
            on_key_press={
                handlers.YesNoKeyPress(self.ecs): callback,
                handlers.DiscardKeyPress(self.ecs): callback,
            },
        )

        return window

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

        buttons_row = self.create_buttons_row(
            self.get_style('ButtonsRow'),
            callback=callback,
            buttons=[
                ['Cancel', False],
                ['OK',     text_input],
            ],
        )

        window = self.create_modal_window(
            self.get_style('Window, Window.modal'),
            width=40,
            height=6,
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
            buttons_row,
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

        msg = self.create(
            widgets.Label, 'Dialog Label',
            msg,
        )

        buttons_row = self.create_buttons_row(
            self.get_style('ButtonsRow'),
            callback=callback,
            buttons=[
                ['Cancel', False],
            ],
        )

        window = self.create_modal_window(
            self.get_style('Window, Window.modal'),
            width=20,
            height= msg.height+buttons.height+len(items)+4,
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
                    self.create_list_separator()
                )
            key_binding = string.ascii_lowercase[index]
            items_list.append_item(
                self.create_list_item(item, key_binding, callback, index)
            )

        window.extend([
            msg,
            decorations.Padded(
                content=items_list,
                padding=Padding(3, 0, 0, 0),
            ),
            buttons_row,
        ])

        widgets_layout = decorations.Padded(
            content=window,
            padding=Padding(8, 0),
        )
        return widgets_layout

    def build(self, widget_type, context):
        # TODO: Move layout definitions to data/ui.yaml ?
        if widget_type == 'YES_NO_PROMPT':
            widgets_layout = self.create_yes_no_prompt(context)

        if widget_type == 'TEXT_INPUT_PROMPT':
            widgets_layout = self.create_text_input_prompt(context)

        if widget_type == 'ALPHABETIC_SELECT_PROMPT':
            widgets_layout = self.create_alphabetic_select_prompt(context)

        if widget_type == 'IN_GAME':
            widgets_layout = containers.Split(bottom=12)

            camera = self.create_window(
                self.get_style('Window'),
                content=render.Camera(self.ecs),
                title='mapcam',
            )

            msg_log = self.create_window(
                self.get_style('Window'),
                content=render.MessageLog(),
                title='logs',
            )

            widgets_layout.extend([camera, msg_log])

        if widget_type == 'MAIN_MENU':
            widgets_layout = containers.Split(top=.4)

            title = basic.Text(
                'Game title!',
                colors=self.default_colors,
                align=Align.CENTER,
            )

            button = self.create_button(
                'Start',
                lambda entity, value: print('!!!', entity, value),
                True,
            )
            button.align = Align.CENTER

            widgets_layout.extend([title, button])

        return widgets_layout

