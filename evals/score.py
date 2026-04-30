#!/usr/bin/env python3
"""Score a tango-bug eval run.

Reads:
  - The work dir's git diff vs the initial commit (the skill's fix)
  - The plan doc (./bug-*.md, excluding bug-report.md) for iteration history
  - Runs symptom + regression tests
  - Greps the diff for known trap patterns
  - Checks the plan's "Root cause" section for expected file paths

Prints a scorecard. Exits 0 on PASS, 1 on TRAP/FAIL/missing.

The harness deliberately avoids being clever: regexes and pytest exit
codes only. The signal we care about is "tests pass + no trap" which
is unambiguous.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def _pytest_cmd() -> list[str]:
    """Pick a pytest invocation that actually has pytest available.

    Order: $PYTEST env var > `pytest` on PATH > `python3 -m pytest`.
    """
    if env := os.environ.get("PYTEST"):
        return shlex.split(env)
    if shutil.which("pytest"):
        return ["pytest"]
    return ["python3", "-m", "pytest"]


def run_pytest(test_dir: Path, work_dir: Path) -> tuple[bool, str]:
    """Run pytest on a directory, return (passed, combined output)."""
    if not test_dir.exists():
        return True, "(no tests)"
    cmd = [*_pytest_cmd(), str(test_dir), "-q", "--tb=short", "--no-header"]
    result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr


def get_diff(work_dir: Path) -> str:
    """Diff vs the initial commit produced by run.sh setup."""
    result = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    return result.stdout


def find_plan_doc(work_dir: Path) -> Path | None:
    """The skill writes ./bug-{branch}-{ts}.md. Pick the newest, ignore bug-report.md."""
    candidates = [
        p for p in work_dir.glob("bug-*.md")
        if p.name != "bug-report.md"
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def extract_section(text: str, heading: str) -> str:
    """Return the body of a top-level '## {heading}' section, up to the next '## '."""
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def count_iterations(section_text: str) -> int:
    return len(re.findall(r"^### Iteration \d+", section_text, re.MULTILINE))


def count_findings(section_text: str) -> dict[str, int]:
    return {
        level: len(re.findall(rf"\[{level}\]", section_text))
        for level in ("P0", "P1", "P2", "P3")
    }


def load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip() for line in path.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--case-dir", required=True, type=Path)
    ap.add_argument("--work-dir", required=True, type=Path)
    args = ap.parse_args()

    print(f"=== Scoring {args.case} ===\n")

    plan_path = find_plan_doc(args.work_dir)
    if plan_path is None:
        print("[FAIL] No plan doc found in work dir.")
        print("       Did /tango-bug actually run? Expected ./bug-*.md.")
        return 1

    plan_text = plan_path.read_text()
    print(f"plan doc:           {plan_path.name}")

    plan_review = extract_section(plan_text, "Codex plan review")
    code_review = extract_section(plan_text, "Codex code review")
    plan_iters = count_iterations(plan_review)
    code_iters = count_iterations(code_review)
    plan_findings = count_findings(plan_review)
    code_findings = count_findings(code_review)
    print(f"plan-review iters:  {plan_iters}  findings={plan_findings}")
    print(f"code-review iters:  {code_iters}  findings={code_findings}")

    correctness = re.findall(
        r"OVERALL:\s*patch is (correct|incorrect)",
        code_review,
        re.IGNORECASE,
    )
    if correctness:
        print(f"final OVERALL:      patch is {correctness[-1]}")

    rc_section = extract_section(plan_text, "Root cause")
    expected_files = load_lines(args.case_dir / "ground-truth-files.txt")
    rc_hits = [f for f in expected_files if f in rc_section]
    if expected_files:
        print(f"root-cause files:   {rc_hits if rc_hits else 'NONE matched'}")

    diff = get_diff(args.work_dir)
    trap_patterns = load_lines(args.case_dir / "trap-patterns.txt")
    trap_hits = [p for p in trap_patterns if re.search(p, diff)]
    print(f"trap patterns:      {trap_hits if trap_hits else 'clean'}")

    symptom_pass, symptom_out = run_pytest(args.work_dir / "tests" / "symptom", args.work_dir)
    regression_pass, regression_out = run_pytest(args.work_dir / "tests" / "regression", args.work_dir)
    print(f"symptom tests:      {'PASS' if symptom_pass else 'FAIL'}")
    print(f"regression tests:   {'PASS' if regression_pass else 'FAIL'}")

    if not symptom_pass:
        print("\n--- symptom output ---")
        print(symptom_out.rstrip())
    if not regression_pass:
        print("\n--- regression output ---")
        print(regression_out.rstrip())

    print()
    if symptom_pass and regression_pass and not trap_hits:
        print("OVERALL: PASS")
        return 0
    if symptom_pass and not regression_pass:
        print("OVERALL: TRAP — symptom fixed but regression broken")
        return 1
    if symptom_pass and trap_hits:
        print("OVERALL: TRAP — symptom fixed but trap pattern matched in diff")
        return 1
    if not symptom_pass:
        print("OVERALL: FAIL — symptom test still failing")
        return 1
    print("OVERALL: UNKNOWN")
    return 1


if __name__ == "__main__":
    sys.exit(main())
