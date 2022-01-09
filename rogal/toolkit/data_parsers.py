from .basic import Decorations

from ..data import data_store, parsers


def parse_decorations(data):
    glyphs = parsers.parse_glyphs_sequence(data)
    if glyphs:
        return Decorations(*glyphs)


def parse_ui_style(data):
    if not data:
        return {}
    style = dict(
        # Common style
        width=data.get('width'),
        height=data.get('height'),
        align=parsers.parse_align(data.get('align')),
        colors=parsers.parse_colors(data),
        # Decorations
        padding=parsers.parse_padding(data.get('padding')),
        decorations=parsers.parse_decorations(data.get('decorations')),
        # Animated
        duration=data.get('duration'),
        frame_duration=data.get('frame_duration'),
        # ProgressBar
        segments=parsers.parse_progress_bar(data.get('segments')),
        reverse=data.get('reverse'),
        # Spinner
        frames=parsers.parse_spinner(data.get('frames')),
        # Separator
        separator=parsers.parse_separator(data.get('separator')),
    )

    # Parsing nested elements - checking if first letter is capitalized
    for element in data.keys():
        if element[0].isupper():
            style[element] = parsers.parse_ui_style(data.get(element))

    style = {
        key: value for key, value in style.items()
        if value is not None
    }
    return style


data_store.register('bitmasks', parsers.parse_glyphs_sequence)
data_store.register('decorations', parse_decorations)
data_store.register('progress_bars', parsers.parse_glyphs_sequence)
data_store.register('separators', parsers.parse_glyphs_sequence)
data_store.register('spinners', parsers.parse_frames_sequence)
data_store.register('ui_style', parse_ui_style, default=dict)

parsers.register('decorations', data_store.decorations.parse)
parsers.register('progress_bar', data_store.progress_bars.parse)
parsers.register('separator', data_store.separators.parse)
parsers.register('spinner', data_store.spinners.parse)
parsers.register('ui_style', data_store.ui_style.parse)

