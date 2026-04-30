from project.backend import get_call_count, reset_call_count
from project.settings import get_settings


def setup_function(_):
    get_settings.cache.clear()
    reset_call_count()


def test_repeated_identical_calls_hit_cache():
    for _ in range(1000):
        get_settings(99, theme="dark", lang="en")

    assert get_call_count() == 1
