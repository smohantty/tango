"""Regression tests: must pass before AND after the fix.

These guard against fixes that disable caching — e.g. clearing the
cache on every call, or removing the @memoize decorator. Such fixes
make the symptom go away but defeat the whole point of the memoize
layer.
"""
from project.backend import get_call_count, reset_call_count
from project.settings import get_settings


def setup_function(_):
    get_settings.cache.clear()
    reset_call_count()


def test_repeated_identical_calls_hit_cache():
    """Backend must be called exactly once for 1000 identical calls."""
    for _ in range(1000):
        get_settings(99, theme="dark", lang="en")

    assert get_call_count() == 1, (
        f"Caching is broken: backend was called {get_call_count()} times "
        f"for 1000 identical inputs"
    )
