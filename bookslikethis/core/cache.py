import functools

from django.conf import settings


def lru_cache(maxsize=None, typed=False):
    """Wraps functools.lru_cache to obey a setting at function call time.

    "settings.CACHE_ENABLED = False" will disable any caching.
    """
    def wrapper(func):
        lru_func = functools.lru_cache(
            maxsize=maxsize, typed=typed)(func)

        def inner(*args, **kwargs):
            if settings.CACHE_ENABLED:
                return lru_func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        # The LRU decorator adds helper methods as attributes
        # of the decorated function itself. Patch those through
        # so no functionality is lost.
        inner.cache_info = lru_func.cache_info
        inner.cache_clear = lru_func.cache_clear
        return functools.update_wrapper(inner, func)

    return wrapper
