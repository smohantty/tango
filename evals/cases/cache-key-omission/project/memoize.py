from functools import wraps


def memoize(fn):
    """Cache results by call arguments."""
    cache = {}

    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = args
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    return wrapper
