from project.backend import get_call_count, reset_call_count
from project.settings import get_settings


def setup_function(_):
    get_settings.cache.clear()
    reset_call_count()


def test_theme_kwarg_respected():
    light = get_settings(42, theme="light")
    assert light["theme"] == "light"

    dark = get_settings(42)  # should default to theme="dark"
    assert dark["theme"] == "dark"


def test_lang_kwarg_respected():
    en = get_settings(7, lang="en")
    assert en["lang"] == "en"

    fr = get_settings(7, lang="fr")
    assert fr["lang"] == "fr"


def test_distinct_kwargs_cache_independently():
    """Different kwargs should each be cached, not collapsed."""
    for _ in range(100):
        get_settings(1, theme="dark")
    for _ in range(100):
        get_settings(1, theme="light")

    assert get_call_count() == 2, (
        f"Expected exactly 2 backend calls (one per distinct theme), "
        f"got {get_call_count()}"
    )
