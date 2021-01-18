import logging

import yaml

from . import rng


log = logging.getLogger(__name__)


DATA_DIR = 'data'


def from_sequence_constructor(loader, node):
    values = loader.construct_sequence(node)
    return rng.RandInt(*values)


class SequenceRepresenter:

    def __init__(self, yaml_tag):
        self.yaml_tag = yaml_tag

    def __call__(self, dumper, data):
        return dumper.represent_sequence(
            self.yaml_tag,
            data.__reduce__[1],
            flow_style=True
        )

for yaml_tag, cls in [
    ('!randint', rng.RandInt),
    ('!randrange', rng.RandRange),
]:
    yaml.add_representer(cls, SequenceRepresenter(yaml_tag))
    yaml.add_constructor(yaml_tag, from_sequence_constructor)


class YAMLDataLoader:

    def load_data(self, fn):
        log.debug(f'Loading data: {fn}')
        with open(self.fn, 'r') as f:
            data = yaml.load(f, yaml.Loader)
            return data

