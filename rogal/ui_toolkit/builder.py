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

    def create_window_title(self, title):
        if title is None:
            return
        # TODO: I don't like this style.pop('padding') approach...
        title_style = self.styles.get('Label.title')
        padding = title_style.pop('padding', None)
        title = widgets.Label(
            text=basic.Text(
                title,
                **self.styles.get('Label.title Text'),
            ),
            frame=basic.Frame(
                **self.styles.get('Label.title Frame'),
            ),
            **title_style,
        )
        if padding:
            title = decorations.Padded(
                content=title,
                padding=padding,
            )

#         title.content.content.renderer = renderers.Blinking(
#             title.content.content.renderer,
#             rate=1200,
#         )

        return title

    def create_window(self, title=None, on_key_press=None):
        window = widgets.Window(
            frame=basic.Frame(
                **self.styles.get('Window Frame'),
            ),
            title=self.create_window_title(title),
            on_key_press=on_key_press,
            **self.styles.get('Window'),
        )
        return window

    def create_modal_window(self, size, title=None, on_key_press=None):
        # NOTE: Extending window size by frame.extents
        #       So basically we only set size of contents, not whole Window
        frame=basic.Frame(
            **self.styles.get('Window Frame'),
        )
        size = Size(
            size.width + frame.extents.width,
            size.height + frame.extents.height,
        )
        window = content=widgets.ModalWindow(
            size=size,
            frame=frame,
            title=self.create_window_title(title),
            on_key_press=on_key_press,
            **self.styles.get('Window'),
            **self.styles.get('Window.modal'),
        )
        return window

    def create_button(self, text, callback, value):
        button = widgets.Button(
            value, callback,
            text=basic.Text(
                text,
                **self.styles.get('Button Text'),
            ),
            frame=basic.Frame(
                **self.styles.get('Button Frame'),
            ),
            # selected_colors=self.default_colors.invert(),
            press_colors=Colors(
                bg="bg",
                fg="BRIGHT_WHITE"
            ),
            selected_renderers=[
                renderers.InvertColors(),
            ],
            **self.styles.get('Button'),
        )
        return button

    def create_buttons_row(self, callback, buttons):
        buttons_row = containers.Row(
            **self.styles.get('Row.buttons'),
        )
        for text, value in buttons:
            buttons_row.append(self.create_button(text, callback, value))
        return buttons_row

    def create_text_input(self, width, text=None):
        text_input = widgets.TextInput(
            self.ecs,
            width=width,
            default_text=text,
            **self.styles.get('TextInput'),
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

        window = self.create_modal_window(
            size=Size(40, 6),
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
            # basic.ProgressBarAnimatedDemo(
            #     value=.75,
            #     width=24,
            #     # height=3,
            #     frame_duration=150,
            #     **self.styles.get('ProgressBar'),
            # ),

            # basic.Spinner(
            #     **self.styles.get('Spinner'),
            # ),

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
            size=Size(40, 6),
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
            size=Size(
                20,
                msg.height+buttons.height+len(items)+4
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
                    self.create_list_separator()
                )
            key_binding = string.ascii_lowercase[index]
            items_list.append_item(
                self.create_list_item(item, key_binding, callback, index)
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

