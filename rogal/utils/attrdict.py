
class AttrDict(dict):

    """Dictionary with attributes access."""

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

