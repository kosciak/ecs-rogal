import collections


Signal = collections.namedtuple(
    'Signal', [
        'source',
        'name',
        'value',
    ])


class SignalsQueue:

    def __init__(self):
        self.signals = collections.deque()

    def put(self, signal):
        self.signals.append(signal)

    def signals_gen(self):
        while self.signals:
            try:
                yield self.signals.popleft()
            except IndexError:
                pass

    def __iter__(self):
        yield from self.signals_gen()

