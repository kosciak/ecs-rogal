from . import data_store, parsers


Glyphs = data_store.glyphs

Charsets = data_store.charsets

Bitmasks = data_store.register('bitmasks', parsers.parse_glyphs_sequence)

Decorations = data_store.register('decorations', parsers.parse_glyphs_sequence)

ProgressBars = data_store.register('progress_bars', parsers.parse_glyphs_sequence)

Spinners = data_store.register('spinners', parsers.parse_frames_sequence)

TilesSources = data_store.tiles_sources

ColorPalettes = data_store.color_palettes

