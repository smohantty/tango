from .backend import fetch_settings_from_db
from .memoize import memoize


@memoize
def get_settings(user_id, *, theme="dark", lang="en"):
    return fetch_settings_from_db(user_id, theme, lang)
