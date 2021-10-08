from ..collections.attrdict import AttrDict
from ..data_loaders import DataLoader


class Data:

    def __init__(self, parse, *loaders):
        self._data = None
        self.parse = parse
        self.loaders = list(loaders)

    def register(self, loader):
        self.loaders.append(loader)
        self._data = None

    def _load(self):
        data = AttrDict()
        for loader in self.loaders:
            if isinstance(loader, str):
                loader = DataLoader(loader)
            for key, value in loader.load().items():
                data[key] = self.parse(value)
        self._data = data

    def get(self, key, default=None, /):
        if self._data is None:
            self._load()
        return self._data.get(key, default)

    # TODO: Some kind of get_or_parse() so we don't need to declare everything by name, 
    #       and just use data structure instead

    def __getattr__(self, key):
        if self._data is None:
            self._load()
        return self._data.get(key)

