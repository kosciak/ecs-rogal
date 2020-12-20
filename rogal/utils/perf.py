from functools import wraps
import time

from decorator import decorator


@decorator
def timeit(func, *args, **kwargs):
    ts = time.time()
    result = func(*args, **kwargs)
    te = time.time()
    print(f'PERF: {func.__name__}({args}, {kwargs}) -> {te-ts:2.4f} sec')
    return result

