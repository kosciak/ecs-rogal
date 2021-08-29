from ..tiles.charsets import Charset, UnicodeBlock


def parse_charset(data):
    return Charset(data)


def parse_unicode_block(data):
    return UnicodeBlock(
        data['from'],
        data['to']
    )

