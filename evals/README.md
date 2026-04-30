# tango-bug evals

Hand-built test cases for measuring whether the `tango-bug` skill
produces high-quality bug fixes — not just symptom-passing ones.

## How a case is structured

Each case lives in `cases/<name>/` and contains:

```
project/                   buggy code (copied to work dir)
tests/                     existing project tests (copied to work dir)
pytest.ini                 (copied to work dir)
bug-report.md              1-2 lines, what you paste to /tango-bug (copied to work dir)
_grader/symptom/           hidden — scorer-only tests that prove the bug is fixed
ground-truth.md            the right fix + acceptable variants + traps
ground-truth-files.txt     paths the plan's "Root cause" should mention
trap-patterns.txt          regexes flagged in the final diff
```

What the skill sees in the work dir: `project/`, `tests/`,
`pytest.ini`, `bug-report.md`. Nothing else. It must reproduce the
bug on its own and decide whether to add a regression test.

What the scorer uses for grading: the work dir's `tests/` (any
project test, including ones the skill added) PLUS the case dir's
`_grader/symptom/` tests, which the scorer runs against the work
dir's `project/` to confirm the bug is actually fixed.

A "fix" that passes the grader's symptom tests but breaks the
project tests is the trap — exactly what the Codex review loop is
supposed to catch.

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
- new test files the skill added under `tests/`
- grader symptom result + project tests result
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

1. Build a `project/` where there's a real bug AND a tempting wrong fix.
2. Put existing project tests under `tests/` for adjacent functionality
   that the trap fix would break. These must pass on the buggy project
   and would fail under the trap. **This is the most important step** —
   without these tests, the case can't distinguish good fixes from
   bad.
3. Put grader symptom tests under `_grader/symptom/` — these are
   hidden from the skill and only run by the scorer. They must fail
   on the buggy project and pass after the correct fix.
4. Verify wiring on the buggy project:
   - `pytest tests` → passes
   - `PYTHONPATH=. pytest _grader/symptom` → fails
5. Write `bug-report.md` (1–2 lines, no reproducer, no test paths),
   `ground-truth.md`, `ground-truth-files.txt`, and
   `trap-patterns.txt`.

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
