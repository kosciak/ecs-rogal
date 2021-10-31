from .core import Align, Padding


def parse_align(data):
    return getattr(Align, data.upper())


def parse_padding(data):
    if isinstance(data, str):
        data = [int(value.strip() or 0) for value in data.split(',')]
    if isinstance(data, int):
        return Padding(data)
    if isinstance(data, (list, tuple)):
        return Padding(*data)
    if isinstance(data, dict):
        return Padding(**data)

