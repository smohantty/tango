# tango

Skills for Claude Code, plus an eval harness that measures whether
they actually produce good results.

## What's here

```
claude/skills/      skills installable into ~/.claude/skills
  tango-bug/          full bug-fix lifecycle with Codex review at plan + diff stages
evals/              hand-built bug cases + scoring harness
setup.sh            install skills into ~/.claude/skills (or ~/.codex/skills)
```

## Install

```bash
./setup.sh claude       # copies every skill in claude/skills/ to ~/.claude/skills/
./setup.sh codex        # same, into ~/.codex/skills/
./setup.sh uninstall    # remove from both
```

Open a fresh Claude Code session afterward and `/tango-bug` will be
live.

## Run an eval

The eval harness measures whether `tango-bug` produces a high-quality
fix — not just one that passes the obvious test. Each case ships with
a *symptom* test (fails before the fix) and a *regression* test
(passes before the fix, designed to fail under a tempting wrong fix).
A good fix passes both.

Requires `pytest`. If it isn't on `PATH`, set `PYTEST=/path/to/pytest`.

```bash
# 1. List available cases
./evals/run.sh list

# 2. Set up an isolated copy of a case
./evals/run.sh setup cache-key-omission
# → creates evals/runs/cache-key-omission/ with project + tests + bug-report.md
#   and an initial git commit of the buggy state

# 3. In a fresh Claude Code session pointed at the work dir, paste
#    bug-report.md and let the skill run end-to-end:
cd evals/runs/cache-key-omission
claude
# > <paste contents of bug-report.md>
# … skill runs investigate → plan → Codex review loop → implement →
#   Codex diff review loop → sanity check, writing ./bug-*.md as it goes.
# When the skill prints "Status: IMPLEMENTED", exit.

# 4. Score the run
cd -
./evals/run.sh score cache-key-omission
```

The scorer prints, in order:

- plan-review and code-review iteration counts and finding counts by
  priority (P0/P1/P2/P3) — signal that Codex caught issues across
  iterations
- the final `OVERALL: patch is correct/incorrect` from Codex
- which expected root-cause file paths the plan named
- any trap-pattern regex hits in the final diff
- symptom + regression test results
- a one-line `OVERALL: PASS / TRAP / FAIL`

`PASS` means the symptom is fixed AND the regression test still
passes AND no trap pattern matched. `TRAP` means the symptom test
passes but a regression broke (or a trap pattern matched) — exactly
the failure mode the Codex review loop is supposed to catch.

## Available cases

| Case                  | Difficulty | What's tricky                                                           |
|-----------------------|------------|-------------------------------------------------------------------------|
| `cache-key-omission`  | medium     | Memoize ignores kwargs; trap fix kills caching                          |
| `mutation-aliasing`   | hard       | Two callers depend on opposite mutation contracts; trap fix breaks one  |

See `evals/README.md` for the full case-design contract and how to
add new cases.
