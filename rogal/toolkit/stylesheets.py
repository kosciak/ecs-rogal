from ..data import data_store


"""Stylesheets related stuff.

CSS / Less / Sass inspired cascading stylesheets mechanism.

Features:
 - <Type>.<classname>:<pseudo-class> selectors, no #<ID> yet
 - Some basic nesting (like Frame and Label inside Button)
 - Invalid properties are ignored

Pseudo-classes:
 :hover     - mouse hovered
 :active    - mouse pressed
 :focus     - with keyboard focus
 :checked   - toggle button with value > 0
 :disabled

"""


SEPARATORS = [
    ':',    # Pseudo-class separator
    '.',    # Classname separator
            # No separator - base selector
]


class StylesheetsManager:

    def __init__(self, ecs=None):
        self._styles = None

    @property
    def styles(self):
        if self._styles is None:
            self._styles = data_store.ui_style
        return self._styles

    def merge(self, source, update):
        """Recursively merge source with update."""
        if not source:
            return update
        if not update:
            return source

        merged = {}
        keys = source.keys() | update.keys()
        for key in keys:
            if key.islower():
                if key in update:
                    merged[key] = update[key]
                else:
                    merged[key] = source[key]
            else:
                merged[key] = self.merge(source.get(key), update.get(key))
        return merged

    def selectors_gen(self, selector):
        selectors = [selector, ]
        for sep in SEPARATORS:
            if sep in selector:
                selector, _, _ = selector.rpartition(sep)
                if selector:
                    selectors.append(selector)
        yield from reversed(selectors)

    def get(self, selector):
        style = {}
        for sel in self.selectors_gen(selector):
            style = self.merge(style, self.styles.get(sel))
        return style

