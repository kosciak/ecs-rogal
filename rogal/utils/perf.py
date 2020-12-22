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

