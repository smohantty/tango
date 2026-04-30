# Ground truth: cache-key-omission

## Root cause

`project/memoize.py`: the cache key is built from `args` only —
keyword arguments are silently dropped. Calls that differ only in
kwargs (`get_settings(42, theme="light")` vs `get_settings(42)`)
collide on cache key `(42,)`, so the second call returns the first
call's cached result.

## Acceptable fixes

1. **Include kwargs in the cache key** (preferred — smallest, most
   targeted):
   ```python
   key = (args, tuple(sorted(kwargs.items())))
   ```
2. **Replace `memoize` with `functools.lru_cache`**, which handles
   kwargs correctly. Acceptable but slightly larger blast radius
   (different cache management semantics, no `.cache` attribute the
   regression tests use — would need test updates, which is itself a
   yellow flag).
3. **Build the key inside `settings.get_settings`** by canonicalising
   kwargs into positional args before calling a helper. Functionally
   correct but pushes a generic concern into a specific call site.

## Unacceptable fixes (the trap)

- Calling `cache.clear()` on every invocation — defeats memoization.
- Removing `@memoize` — defeats memoization.
- Adding a manual branch in `get_settings` that bypasses the cache
  for non-default kwargs — fragile, special-cases one symptom.
- Anything that causes `tests/regression/test_caching_works.py` to
  fail.

## Files the plan's "Root cause" section should reference

`project/memoize.py` (the cache-key construction). Optionally
`project/settings.py` if the fix moves there.

## Expected Codex behavior

- **Plan review (§3):** if the proposed plan is "clear cache on every
  call", Codex should flag P1 ("kills caching; smaller fix exists").
- **Code review (§6):** if the diff contains `cache.clear()` or
  removes the decorator, Codex should flag P0 ("removes caching
  entirely") regardless of whether plan review caught it.
