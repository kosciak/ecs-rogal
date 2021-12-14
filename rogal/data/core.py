from ..collections.attrdict import AttrDict

from .loaders import DataLoader


class Data:

    def __init__(self, name, parse, default=None, /, *loaders):
        self.name = name # NOTE: Just in case it would be handy for debugging
        self._data = None
        self._parse = parse
        self._default = default
        self.loaders = list(loaders)

    def register(self, loader):
        self.loaders.append(loader)
        self._data = None

    def _load(self):
        self._data = AttrDict()
        for loader in self.loaders:
            if isinstance(loader, str):
                loader = DataLoader(loader)
            for key, value in loader.load().items():
                self._data[key] = self.parse(value)

    def get(self, key, default=None, /):
        if self._data is None:
            self._load()
        return self._data.get(key, default or (self._default and self._default()))

    def parse(self, data):
        # If it's a name just return data, parse otherwise
        if isinstance(data, str):
            value = self.get(data)
            if value is not None:
                return value
        return self._parse(data)

    def __getattr__(self, key):
        return self.get(key)

    def __iter__(self):
        if self._data is None:
            self._load()
        yield from self._data


class DataParsers(AttrDict):

    def register(self, name, parser):
        # TODO: Keep name, so we can automate parsing? 
        #       Like: parse(node_name, data) -> parse using parser by node_name
        self['parse_%s' % name] = parser


class DataStore(AttrDict):

    def register(self, name, parser, default=None):
        data = Data(name, parser, default)
        self[name] = data
        return data

    def register_source(self, **kwargs):
        if 'data' in kwargs:
            data = kwargs.pop('data')
            loader = DataLoader(data)
            kwargs.update(loader.load())

        for name, loader in kwargs.items():
            # name = name.title().replace('_', '')
            data = self.get(name)
            if isinstance(loader, (list, tuple)):
                for l in loader:
                    data.register(l)
            else:
                data.register(loader)

