import atexit
import collections
from functools import wraps
import logging
import time
import types

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
        if isinstance(name, (types.MethodType, types.FunctionType)):
            # Use fully qualified method/function names
            name = f'{name.__module__}.{name.__qualname__}()'
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

    @classmethod
    def stats(cls, name=None):
        if not name:
            log.debug('Perf stats:')
            for name in sorted(cls._PERF_STATS.keys()):
                cls.stats(name)
            return
        times = cls._PERF_STATS[name]
        total = sum(times)
        avg = total / len(times)
        med = sorted(times)[len(times)//2]
        log.debug(f'{name:60s} - calls: {len(times):7d}   avg: {avg:2.4f}   med: {med:2.4f}   max: {max(times):2.4f}   total: {total:2.4f}')

atexit.register(Perf.stats)
