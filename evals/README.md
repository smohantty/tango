# tango-bug evals

Hand-built test cases for measuring whether the `tango-bug` skill
produces high-quality bug fixes — not just symptom-passing ones.

## How a case is structured

Each case lives in `cases/<name>/` and contains:

```
project/                   buggy code
tests/symptom/             FAIL before fix, PASS after  (proves the bug exists)
tests/regression/          PASS before fix, PASS after  (catches "fixes" that break things)
pytest.ini
bug-report.md              what you paste to /tango-bug
ground-truth.md            the right fix + acceptable variants + traps
ground-truth-files.txt     paths the plan's "Root cause" should mention
trap-patterns.txt          regexes flagged in the final diff
```

The two test suites are the real grading. Symptom tests confirm the
fix lands; regression tests confirm it didn't ship at the cost of
adjacent behavior. A "fix" that passes symptom but fails regression
is the trap — exactly what the Codex review loop is supposed to
catch.

## Running a case

Requires `pytest` available — set `PYTEST` if it isn't on PATH:

```bash
export PYTEST="/path/to/venv/bin/pytest"   # or just leave unset
```

Workflow:

```bash
# 1. set up an isolated copy of the case
./run.sh setup cache-key-omission

# 2. open a fresh Claude Code session in the work dir
cd runs/cache-key-omission
claude   # then paste bug-report.md and let /tango-bug run

# 3. when the skill reports "Status: IMPLEMENTED", come back and score
cd ../..
./run.sh score cache-key-omission
```

The scorer prints:

- plan-review and code-review iteration counts and finding counts
  by priority (signal: did Codex catch P0/P1 issues at iteration 1?)
- final `OVERALL: patch is correct/incorrect` verdict
- which expected root-cause files the plan named
- any trap-pattern regex matches in the final diff
- symptom + regression test outcomes
- a one-line OVERALL: PASS / TRAP / FAIL

## Cases

### `cache-key-omission` (medium)

A memoize decorator caches by `args` only, ignoring `kwargs`. Calls
that differ only in keyword arguments collide on the cache key.

**The trap:** "fix" by clearing the cache on every call. Symptom
goes away (each call goes to backend with correct kwargs), but the
regression test fails (1000 identical calls now produce 1000 backend
hits instead of 1).

### `mutation-aliasing` (hard)

`apply_promotion(items, promo)` mutates items in place. `checkout.py`
relies on the mutation. `audit.py` accidentally feeds it a live cart
reference, mutating the real cart during what should be a read-only
audit.

**The trap:** "fix" by making `apply_promotion` non-mutating without
updating `checkout.py`. Audit symptom goes away, but checkout
regression tests fail because the discount return value is silently
discarded — cart total stays at the original price.

## Adding a case

1. Build a project where there's a real bug AND a tempting wrong fix.
2. Write a symptom test that fails on the bug.
3. Write a regression test that passes pre-fix and would fail under
   the trap fix. **This is the most important step** — without it,
   your case can't distinguish good fixes from bad.
4. Verify the wiring with `pytest tests/symptom` (fails) and
   `pytest tests/regression` (passes) on the buggy project.
5. Write `ground-truth.md`, `ground-truth-files.txt`,
   `trap-patterns.txt`, and `bug-report.md`.

## What the eval does NOT do (yet)

- No headless invocation of `/tango-bug` — you run it manually in a
  fresh Claude Code session per case. This is intentional for now:
  the skill spawns Codex subagents and the harness invocation path
  for that is fiddlier than it's worth at v1.
- No LLM-judge of plan quality. The scorer only checks for hard
  evidence: tests + regex + iteration counts. A fix that passes
  both test suites and contains no trap patterns is graded PASS
  even if the plan doc is sloppy.
- No aggregation across runs. Run cases one at a time.
