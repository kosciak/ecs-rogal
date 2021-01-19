import logging

import yaml

from . import rng


log = logging.getLogger(__name__)


DATA_DIR = 'data'


class Constructor:

    def __init__(self, klass):
        self.klass = klass

class Representer:

    def __init__(self, yaml_tag):
        self.yaml_tag = yaml_tag


class SequenceConstructor(Constructor):

    def __call__(self, loader, node):
        values = loader.construct_sequence(node)
        return self.klass(*values)

class SequenceRepresenter(Representer):

    def __call__(self, dumper, data):
        return dumper.represent_sequence(
            self.yaml_tag,
            data.__reduce__[1],
            flow_style=True
        )

def register_sequence(yaml_tag, klass):
    yaml.add_representer(klass, SequenceRepresenter(yaml_tag))
    yaml.add_constructor(yaml_tag, SequenceConstructor(klass))


class ScalarConstructor(Constructor):

    def __call__(self, loader, node):
        value = loader.construct_scalar(node)
        return self.klass.parse(value)

class ScalarRepresenter(Representer):

    def __call__(self, dumper, data):
        return dumper.represent_scalar(self.yaml_tag, str(data))

def register_scalar(yaml_tag, klass):
    yaml.add_representer(klass, ScalarRepresenter(yaml_tag))
    yaml.add_constructor(yaml_tag, ScalarConstructor(klass))


register_sequence('!randint', rng.RandInt)
register_sequence('!randrange', rng.RandRange)
register_scalar('!dice', rng.Dice)


class YAMLDataLoader:

    def load_data(self, fn):
        log.debug(f'Loading data: {fn}')
        with open(self.fn, 'r') as f:
            data = yaml.load(f, yaml.Loader)
            return data

