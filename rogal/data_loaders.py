import logging

import yaml


log = logging.getLogger(__name__)


DATA_DIR = 'data'


class YAMLDataLoader:

    def load_data(self, fn):
        log.debug(f'Loading data: {fn}')
        with open(self.fn, 'r') as f:
            data = yaml.safe_load(f)
            return data

