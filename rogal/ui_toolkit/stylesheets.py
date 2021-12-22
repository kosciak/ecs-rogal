from ..data import data_store


class StylesheetsManager:

    def __init__(self):
        self.styles = data_store.ui_style

    def get(self, selector):
        style = {}
        base, sep, classname = selector.rpartition('.')
        if base:
            style.update(
                self.styles.get(base)
            )
        style.update(
            self.styles.get(selector)
        )
        return style

