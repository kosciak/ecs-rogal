from ..collections.attrdict import DefaultAttrDict

from ..data import data_store, parsers

from .keys import Key


def parse_keys(data):
    return list(map(Key.parse, data))


def parse_key_bindings(data):
    key_bindings = DefaultAttrDict(set)
    for name, keys in data.items():
        key_bindings[name] = parsers.parse_keys(keys)
    return key_bindings


data_store.register('key_bindings', parse_key_bindings)

parsers.register('keys', parse_keys)
parsers.register('key_bindings', parse_key_bindings)

