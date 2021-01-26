import atexit
import collections
from functools import wraps
import logging
import time

from decorator import decorator


log = logging.getLogger(__name__)


@decorator
def timeit(func, *args, **kwargs):
    ts = time.time()
    result = func(*args, **kwargs)
    te = time.time()
    log.debug(f'PERF: {func.__name__}({args}, {kwargs}) -> {te-ts:2.4f} sec')
    return result


class Perf:

    _PERF_STATS = collections.defaultdict(list)

    __slots__ = ('name', 'start', )

    def __init__(self, name):
        self.name = name
        self.start = time.time()

    def elapsed(self):
        elapsed = time.time() - self.start
        self._PERF_STATS[self.name].append(elapsed)
        return elapsed

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.elapsed()


def perf_stats(name=None):
    if not name:
        log.debug('Perf stats:')
        for name in sorted(Perf._PERF_STATS.keys()):
            perf_stats(name)
        return
    times = Perf._PERF_STATS[name]
    avg = sum(times) / len(times)
    med = sorted(times)[len(times)//2]
    log.debug(f'{name} - calls: {len(times)}, avg: {avg:2.4f}, med: {med:2.4f}, max: {max(times):2.4f}')

atexit.register(perf_stats)
