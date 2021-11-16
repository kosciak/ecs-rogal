from ..data import data_store, parsers


data_store.register('bitmasks', parsers.parse_glyphs_sequence)
data_store.register('decorations', parsers.parse_glyphs_sequence)
data_store.register('progress_bars', parsers.parse_glyphs_sequence)
data_store.register('separators', parsers.parse_glyphs_sequence)
data_store.register('spinners', parsers.parse_frames_sequence)

parsers.register('decorations', data_store.decorations.parse)
parsers.register('progress_bar', data_store.progress_bars.parse)
parsers.register('separator', data_store.separators.parse)
parsers.register('spinner', data_store.spinners.parse)

