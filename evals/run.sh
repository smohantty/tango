#!/usr/bin/env bash
# Tango-bug eval harness.
#
#   ./run.sh setup <case>     copy a case to runs/<case>/, init git
#   ./run.sh score <case>     run tests + parse plan, print scorecard
#   ./run.sh list             list available cases
#
# Workflow:
#   1. ./run.sh setup cache-key-omission
#   2. cd runs/cache-key-omission
#   3. open a fresh Claude Code session here
#   4. paste bug-report.md and let /tango-bug run end-to-end
#   5. cd back; ./run.sh score cache-key-omission

set -euo pipefail

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
CASES_DIR="$EVAL_DIR/cases"
RUNS_DIR="$EVAL_DIR/runs"

usage() {
    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
}

cmd_list() {
    if [ ! -d "$CASES_DIR" ]; then
        echo "No cases directory."
        return
    fi
    for d in "$CASES_DIR"/*/; do
        [ -d "$d" ] || continue
        echo "  $(basename "$d")"
    done
}

cmd_setup() {
    local case_name="${1:?case name required}"
    local case_dir="$CASES_DIR/$case_name"
    local work_dir="$RUNS_DIR/$case_name"

    if [ ! -d "$case_dir" ]; then
        echo "Unknown case: $case_name" >&2
        echo "Available cases:" >&2
        cmd_list >&2
        exit 1
    fi

    rm -rf "$work_dir"
    mkdir -p "$work_dir"

    cp -r "$case_dir/project" "$work_dir/"
    cp -r "$case_dir/tests" "$work_dir/"
    cp "$case_dir/pytest.ini" "$work_dir/"
    cp "$case_dir/bug-report.md" "$work_dir/"

    (
        cd "$work_dir"
        git init -q -b main
        git add -A
        git -c user.email=eval@local -c user.name=eval-harness \
            commit -q -m "initial buggy state for $case_name"
    )

    cat <<EOF
Case '$case_name' set up at:
  $work_dir

Next steps:
  1. cd $work_dir
  2. Open a Claude Code session in that directory.
  3. Paste the contents of bug-report.md and let /tango-bug run end-to-end.
  4. When the skill reports "Status: IMPLEMENTED", come back and run:
     $0 score $case_name
EOF
}

cmd_score() {
    local case_name="${1:?case name required}"
    local case_dir="$CASES_DIR/$case_name"
    local work_dir="$RUNS_DIR/$case_name"

    if [ ! -d "$work_dir" ]; then
        echo "No run found at $work_dir. Did you run setup?" >&2
        exit 1
    fi

    python3 "$EVAL_DIR/score.py" \
        --case "$case_name" \
        --case-dir "$case_dir" \
        --work-dir "$work_dir"
}

case "${1:-}" in
    setup) shift; cmd_setup "$@" ;;
    score) shift; cmd_score "$@" ;;
    list)  cmd_list ;;
    *) usage ;;
esac
