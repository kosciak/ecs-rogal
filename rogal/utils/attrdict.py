import collections


class AttrMixin:

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value


class AttrDict(AttrMixin, dict):

    """Dictionary with attributes access."""

    pass


class DefaultAttrDict(AttrMixin, collections.defaultdict):

    """Default dict with attributes access."""

    def __getattr__(self, name):
        return self[name]

