#!/usr/bin/env bash
# Install every skill in claude/skills/ at the user level for the chosen agent.
# Always copies (no symlink). Always overwrites any existing install at the destination.
#
# Usage:
#   ./setup.sh claude     # install all skills for Claude Code
#   ./setup.sh codex      # install all skills for Codex
#   ./setup.sh uninstall  # remove every skill in claude/skills/ from both agents

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_ROOT/claude/skills"

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "Expected skills directory not found: $SKILLS_SRC" >&2
  exit 3
fi

cmd="${1:-}"

if [[ -z "$cmd" || "$cmd" == "-h" || "$cmd" == "--help" ]]; then
  sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
fi

dest_root_for() {
  case "$1" in
    claude) echo "$HOME/.claude/skills" ;;
    codex)  echo "$HOME/.codex/skills" ;;
    *)      echo "" ;;
  esac
}

discover_skills() {
  local found=0
  for skill_dir in "$SKILLS_SRC"/*/; do
    if [[ -f "$skill_dir/SKILL.md" ]]; then
      basename "$skill_dir"
      found=1
    fi
  done
  if [[ "$found" == "0" ]]; then
    echo "No skills found in $SKILLS_SRC (looked for */SKILL.md)" >&2
    exit 3
  fi
}

if [[ "$cmd" == "uninstall" ]]; then
  removed=0
  while IFS= read -r skill_name; do
    for agent in claude codex; do
      dest="$(dest_root_for "$agent")/$skill_name"
      if [[ -e "$dest" || -L "$dest" ]]; then
        rm -rf "$dest"
        echo "Removed: $dest"
        removed=1
      fi
    done
  done < <(discover_skills)
  if [[ "$removed" == "0" ]]; then
    echo "Nothing to remove."
  fi
  exit 0
fi

agent="$cmd"
dest_root="$(dest_root_for "$agent")"
if [[ -z "$dest_root" ]]; then
  echo "Unknown command: $cmd" >&2
  echo "Run: ./setup.sh [claude|codex|uninstall]" >&2
  exit 1
fi

mkdir -p "$dest_root"

count=0
while IFS= read -r skill_name; do
  src="$SKILLS_SRC/$skill_name"
  dest="$dest_root/$skill_name"
  rm -rf "$dest"
  cp -R "$src" "$dest"
  echo "Installed $skill_name → $dest"
  count=$((count + 1))
done < <(discover_skills)

echo
echo "Installed $count skill(s) for agent: $agent"
echo "Open a fresh session and the skills will be available."
