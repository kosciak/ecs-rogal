from ..tiles.tilesheets import Tilesheet


class TilesheetParser:

    def __init__(self, charsets):
        self.charsets = charsets

    def __call__(self, data):
        return Tilesheet(
            data['path'],
            data['columns'],
            data['rows'],
            self.charsets.get(data['charset']),
        )

