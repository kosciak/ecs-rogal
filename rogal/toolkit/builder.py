import string

from ..data import Decorations, ProgressBars, Spinners
from ..geometry import Size

from ..events import handlers

from .. import render

from ..console.core import Align, Padding, Colors

from .stylesheets import StylesheetsManager
from . import basic
from . import containers
from . import decorations
from . import separators
from . import renderers
from . import widgets
from . import labels
from . import buttons
from . import windows


# TODO: Scrollable Panels?


class WidgetsBuilder:

    def __init__(self, ecs):
        self.ecs = ecs
        self.stylesheets = StylesheetsManager()
        self.default_colors = Colors("fg", "bg")

    def get_style(self, selectors):
        return self.stylesheets.get(selectors)

    def create(self, element_cls, style=None, *args, **kwargs):
        if isinstance(style, str):
            style = self.get_style(style)
        style = style or {}
        element = element_cls(
            *args,
            **kwargs,
            **style,
        )
        return element

    def set_style(self, element, style):
        if isinstance(style, str):
            style = self.get_style(style)
        style = style or {}
        element.set_style(**style)

    def create_framed_label(self, style, txt):
        if txt is None:
            return

        label = labels.Label(
            txt=txt,
        )
        framed_label = labels.FramedLabel(
            label=label,
            **style,
        )

        return framed_label

    def create_window(self, style, content, title=None, on_key_press=None):
        window = windows.Window(
            content=content,
            on_key_press=on_key_press,
            **style,
        )

        title = self.create_framed_label(
            self.get_style('.title'),
            txt=title,
        )
        window.title = title

        return window

    def create_modal_window(self, style, content, title=None, on_key_press=None):
        window = windows.Window(
            content=content,
            on_key_press=on_key_press,
            **style,
        )
        window.default_z_order=500

        title = self.create_framed_label(
            self.get_style('.title'),
            txt=title,
        )
        window.title = title

        close_button = self.create_label_button(
            self.get_style('.close_button'),
            txt='X',
        )
        window.overlay.close_button = close_button
        close_button.on('clicked', window.on_close)

        return window

    def create_toggle_labels(self, toggle_labels):
        content = []
        for txt in toggle_labels:
            label = labels.Label(
                txt,
            )
            content.append(label)
        return content

    def create_checkbox(self, style, value=None):
        labels = self.create_toggle_labels(
            [' ', 'x'],
        )
        button = buttons.CheckButton(
            content=labels,
            value=value,
            **style,
        )
        return button

    def create_radio(self, style, group, value=None):
        labels = self.create_toggle_labels(
            [' ', 'o'],
        )
        button = buttons.RadioButton(
            content=labels,
            group=group,
            value=value,
            **style,
        )
        return button

    def create_label_button(self, style, txt):
        label = labels.Label(
            txt=txt,
        )
        button = buttons.Label(
            content=label,
            **style,
        )
        return button

    def create_button(self, style, txt, callback, value):
        label = labels.Label(
            txt,
        )
        button = buttons.Button(
            content=label,
            callback=callback,
            value=value,
            # selected_colors=self.default_colors.invert(),
            press_colors=Colors(
                bg="bg",
                fg="BRIGHT_WHITE"
            ),
            selected_renderers=[
                renderers.InvertColors(),
            ],
            **style,
        )
        return button

    def create_buttons_row(self, style, callback, buttons):
        buttons_row = widgets.ButtonsRow(**style)

        for text, value in buttons:
            button = self.create_button(
                self.get_style('.button'),
                text,
                callback, value,
            )
            buttons_row.append(button)

        # self.set_style(buttons_row, style)
        return buttons_row

    def create_text_input(self, width, text=None):
        text_input = self.create(
            widgets.TextInput, 'TextInput',
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

    def create_horizontal_separator(self):
        separator = decorations.Padded(
            content=separators.HorizontalSeparator(
                segments=separators.SeparatorSegments([
                    0x2500, 0x251c, 0x2524,
                ]),
            ),
            padding=Padding(0, -1),
        )

        # separator = separators.HorizontalSeparator(
        #     separators.SeparatorSegments('-><'),
        #     width=10,
        #     align=Align.CENTER,
        # )

        return separator

    def create_yes_no_prompt(self, context):
        title = context['title']
        msg = context['msg']
        callback = context['callback']

        msg = labels.Label(
            txt=msg,
            **self.get_style('Dialog Label'),
        )
        # self.set_style(msg, 'Dialog Label')

        buttons_row = self.create_buttons_row(
            self.get_style('ButtonsRow'),
            callback=callback,
            buttons=[
                ['No',  False],
                ['Yes', True],
            ],
        )

        checkbox = self.create_checkbox(
            self.get_style('.checkbox'),
        )
        checkbox_label = self.create_label_button(
            self.get_style('.label'),
            'checkbox',
        )
        checkbox.set_label(checkbox_label)

        radio_group = buttons.ButtonsGroup()
        radio1 = self.create_radio(
            self.get_style('.radio'),
            radio_group, value=1,
        )
        radio1_label = self.create_label_button(
            self.get_style('.label'),
            'radio 1',
        )
        radio1.set_label(radio1_label)

        radio2 = self.create_radio(
            self.get_style('.radio'),
            radio_group,
        )
        radio2_label = self.create_label_button(
            self.get_style('.label'),
            'radio 2',
        )
        radio2.set_label(radio2_label)

        toggle_buttons = containers.List([
            containers.Row([
                checkbox, checkbox_label,
            ]),
            containers.Row([
                radio1, radio1_label,
            ]),
            containers.Row([
                radio2, radio2_label,
            ]),
        ])

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

        content = containers.List(
            content=[
                # progress_bar,
                # spinner,
                msg,
                self.create_horizontal_separator(),
                toggle_buttons,
                self.create_horizontal_separator(),
                buttons_row,
            ],
            width=40,
        )

        window = self.create_modal_window(
            self.get_style('Window.modal'),
            content=content,
            title=title,
            on_key_press=[
                handlers.YesNoKeyPress(callback),
                handlers.DiscardKeyPress(callback),
            ],
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
            on_key_press=[
                handlers.OnKeyPress('common.SUBMIT', callback, text_input),
                handlers.DiscardKeyPress(callback),
            ],
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
            labels.Label, 'Dialog Label',
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
            on_key_press=[
                handlers.DiscardKeyPress(callback),
            ],
        )

        items_list = widgets.ListBox(
            align=Align.TOP_LEFT,
        )
        # TODO: Move to create_list()
        for index, item in enumerate(items):
            if index == len(items) / 2:
                items_list.append_separator(
                    self.create_horizontal_separator()
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

            content = containers.Split(
                content=[
                    camera,
                    msg_log,
                ],
                bottom=12,
            )

            # TODO: widgets.Screen?
            widgets_layout = windows.Window(
                content=content,
                colors=None,
            )

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

