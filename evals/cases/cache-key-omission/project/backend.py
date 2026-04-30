_call_count = {"n": 0}


def fetch_settings_from_db(user_id, theme, lang):
    """Pretend this is an expensive DB lookup."""
    _call_count["n"] += 1
    return {
        "user_id": user_id,
        "theme": theme,
        "lang": lang,
        "loaded": True,
    }


def reset_call_count():
    _call_count["n"] = 0


def get_call_count():
    return _call_count["n"]
