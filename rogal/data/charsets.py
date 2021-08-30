from ..tiles.charsets import Charset, UnicodeBlock


def parse_charset(data):
    if 'code_points' in data:
        return Charset(data['code_points'])
    elif 'from' in data and 'to' in data:
        return UnicodeBlock(
            data['from'],
            data['to']
        )

