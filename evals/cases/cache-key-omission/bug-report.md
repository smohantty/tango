# Bug report

When I call `get_settings(42, theme="light")` and then later call
`get_settings(42)` (which should default to `theme="dark"`), the second
call returns the light settings instead of dark. This is breaking our
theme switcher.

## Reproducer

```python
from project.settings import get_settings

print(get_settings(42, theme="light"))
# {'user_id': 42, 'theme': 'light', 'lang': 'en', 'loaded': True}

print(get_settings(42))
# expected: {..., 'theme': 'dark', ...}
# actual:   {..., 'theme': 'light', ...}
```

## Tests

- `tests/symptom/` — currently failing tests demonstrating the bug.
- `tests/regression/` — tests that should keep passing after the fix
  (these guard against fixes that throw the baby out with the bath
  water).

Please investigate and fix end-to-end with `/tango-bug`.
