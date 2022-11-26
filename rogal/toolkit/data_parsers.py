from ..data import data_store, parsers


def parse_size_value(data):
    if isinstance(data, str) and data.endswith('%'):
        fraction = int(data[:data.find('%')])
        if fraction == 100:
            return 0
        return  fraction / 100.
    return data


def parse_ui_style(data):
    if not data:
        return {}
    style = dict(
        # Common style
        width=parsers.parse_width(data.get('width')),
        height=parsers.parse_height(data.get('height')),
        align=parsers.parse_align(data.get('align')),
        colors=parsers.parse_colors(data.get('colors') or data),
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
    for key in data.keys():
        if not key.islower():
            style[key] = parsers.parse_ui_style(data.get(key))

    style = {
        key: value for key, value in style.items()
        if value is not None
    }
    return style


data_store.register('bitmasks', parsers.parse_glyphs_sequence)
data_store.register('decorations', parsers.parse_glyphs_sequence)
data_store.register('progress_bars', parsers.parse_glyphs_sequence)
data_store.register('separators', parsers.parse_glyphs_sequence)
data_store.register('spinners', parsers.parse_frames_sequence)
data_store.register('ui_style', parse_ui_style)

parsers.register('width', parse_size_value)
parsers.register('height', parse_size_value)

parsers.register('decorations', data_store.decorations.parse)
parsers.register('progress_bar', data_store.progress_bars.parse)
parsers.register('separator', data_store.separators.parse)
parsers.register('spinner', data_store.spinners.parse)
parsers.register('ui_style', data_store.ui_style.parse)

