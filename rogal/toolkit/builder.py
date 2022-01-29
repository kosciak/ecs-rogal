import string

from ..data import Decorations, ProgressBars, Spinners
from ..geometry import Size

from ..events import handlers

from .. import render

from ..console.core import Align, Padding, Colors

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
        self._stylesheets = None
        self.default_colors = Colors("fg", "bg") # TODO: Remove

    @property
    def stylesheets(self):
        if self._stylesheets is None:
            self._stylesheets = self.ecs.resources.stylesheets_manager
        return self._stylesheets

    def get_style(self, selectors):
        return self.stylesheets.get(selectors)

    def create(self, element_cls, style=None, *args, **kwargs):
        if isinstance(style, str):
            style = self.get_style(style)
        style = style or {}
        element = element_cls(
            style=style,
            *args,
            **kwargs,
        )
        return element

    def set_style(self, element, style):
        if isinstance(style, str):
            style = self.get_style(style)
        style = style or {}
        element.set_style(**style)

    def create_framed_label(self, txt, selector=None):
        if txt is None:
            return

        label = labels.Label(
            txt=txt,
        )
        framed_label = labels.FramedLabel(
            label=label,
            selector=selector,
            style=self.get_style(selector),
        )

        return framed_label

    def create_window(self, content, title=None, selector=None):
        title = self.create_framed_label(
            txt=title,
            selector='.title',
        )

        window = windows.Window(
            content=content,
            title=title,
            selector=selector,
            style=self.get_style(selector),
        )

        return window

    def create_dialog_window(self, content, title=None, selector=None):
        title = self.create_framed_label(
            txt=title,
            selector='.title',
        )

        close_button = self.create_label_button(
            txt='X',
            selector='.close_button',
        )

        window = windows.DialogWindow(
            content=content,
            title=title,
            close_button=close_button,
            # post_renderers=[renderers.InvertColors(), ],
            selector=selector,
            style=self.get_style(selector),
        )
        window.default_z_order=500

        return window

    def create_toggle_labels(self, toggle_labels):
        content = []
        for txt in toggle_labels:
            label = labels.Label(
                txt,
            )
            content.append(label)
        return content

    def create_checkbox(self, value=None, selector=None):
        labels = self.create_toggle_labels(
            [' ', 'x'],
        )
        button = buttons.CheckButton(
            content=labels,
            value=value,
            selector=selector,
            style=self.get_style(selector),
        )
        return button

    def create_radio(self, group, value=None, selector=None):
        labels = self.create_toggle_labels(
            [' ', 'o'],
        )
        button = buttons.RadioButton(
            content=labels,
            group=group,
            value=value,
            selector=selector,
            style=self.get_style(selector),
        )
        return button

    def create_label_button(self, txt, selector=None):
        label = labels.Label(
            txt=txt,
        )
        button = buttons.Label(
            content=label,
            selector=selector,
            style=self.get_style(selector),
        )
        return button

    def create_button(self, txt, selector=None):
        label = labels.Label(
            txt,
        )
        button = buttons.Button(
            content=label,
            selector=selector,
            style=self.get_style(selector),
        )
        return button

    def create_buttons_row(self, callback, buttons, selector=None):
        buttons_row = widgets.ButtonsRow(
            selector=selector,
            style=self.get_style(selector),
        )

        for text, value in buttons:
            button = self.create_button(
                text,
                callback, value,
                selector='.button',
            )
            buttons_row.append(button)

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

    def create_horizontal_separator(self, selector=None):
        separator = decorations.Padded(
            content=separators.HorizontalSeparator(
                style=dict(
                    segments=separators.SeparatorSegments([
                        0x2500, 0x251c, 0x2524,
                    ]),
                ),
            ),
            style=dict(
                padding=Padding(0, -1),
            ),
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

        msg = labels.Label(
            txt=msg,
            style=self.get_style('Dialog Label'),
        )

        checkbox = self.create_checkbox(
            selector='.checkbox',
        )
        checkbox_label = self.create_label_button(
            'checkbox',
            selector='.label',
        )
        checkbox_label.assign(checkbox)

        radio_group = buttons.ButtonsGroup()
        radio1 = self.create_radio(
            radio_group, value=1,
            selector='.radio',
        )
        radio1_label = self.create_label_button(
            'radio 1',
            selector='.label',
        )
        radio1_label.assign(radio1)

        radio2 = self.create_radio(
            radio_group,
            selector='.radio',
        )
        radio2_label = self.create_label_button(
            'radio 2',
            selector='.label',
        )
        radio2_label.assign(radio2)

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

        progress_bar = basic.ProgressBarAnimatedDemo(
            value=.75,
            frame_duration=150,
            style=self.get_style('ProgressBar'),
        )

        spinner = basic.Spinner(
            style=self.get_style('Spinner'),
        )

        content = containers.List(
            content=[
                # progress_bar,
                # spinner,
                msg,
                self.create_horizontal_separator(),
                toggle_buttons,
                self.create_horizontal_separator(),
            ],
        )

        dialog = self.create_dialog_window(
            content=content,
            title=title,
            selector='Window.dialog',
        )

        dialog_buttons = [
            ['No',  False, 'dialog.NO'],
            ['Yes', True, 'dialog.YES'],
        ]

        for text, value, key_binding in dialog_buttons:
            button = self.create_button(
                text,
                selector='.button',
            )
            dialog.add_button(button, value, key_binding)

        return dialog

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
            callback=callback,
            buttons=[
                ['Cancel', False],
                ['OK',     text_input],
            ],
            selector='ButtonsRow',
        )

        window = self.create_dialog_window(
            width=40,
            height=6,
            title=title,
            on_key_press=[
                handlers.OnKeyPress('common.SUBMIT', callback, text_input),
                handlers.DiscardKeyPress(callback),
            ],
            selector='Window.dialog',
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
            callback=callback,
            buttons=[
                ['Cancel', False],
            ],
            selector='ButtonsRow',
        )

        window = self.create_dialog_window(
            width=20,
            height= msg.height+buttons.height+len(items)+4,
            title=title,
            on_key_press=[
                handlers.DiscardKeyPress(callback),
            ],
            selector='Window.dialog',
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
                content=render.Camera(self.ecs),
                title='mapcam',
                selector='Window',
            )

            msg_log = self.create_window(
                content=render.MessageLog(),
                title='logs',
                selector='Window',
            )

            content = containers.Split(
                content=[
                    camera,
                    msg_log,
                ],
                bottom=12,
            )

            widgets_layout = widgets.Screen(
                content=content,
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

