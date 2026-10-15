#!/bin/bash

# UW Slides Lint Script
# Runs deterministic checks on a deck: missing fragments, aria-label, alt text,
# CSS scoping, font sizes, stale briefs, and brief/deck.yml cross-file checks.
#
# Usage: ./lint.sh [--strict] [--format json] [deck-dir]
#   --strict   exit 1 on warnings as well as errors (default: only errors)
#   --format json  machine-readable JSON output
#   deck-dir   path to the deck (default: current directory)
#
# tools/lint.py is found in this order:
#   1. <deck>/tools/lint.py (vendored by /uw-slides:new-deck)
#   2. $UW_SLIDES_HOME/tools/lint.py
#   3. ~/.claude/plugins/local/uw-slides/tools/lint.py
#
# Recommended Claude Code allow rule: Bash(python3 tools/lint.py *)

set -e

ARGS=()
DECK_DIR="."
for arg in "$@"; do
  case "$arg" in
    --strict|--format|json) ARGS+=("$arg") ;;
    *) DECK_DIR="$arg" ;;
  esac
done

# Locate tools/lint.py
LINTER=""
for candidate in \
    "$DECK_DIR/tools/lint.py" \
    "${UW_SLIDES_HOME:+$UW_SLIDES_HOME/tools/lint.py}" \
    "$HOME/.claude/plugins/local/uw-slides/tools/lint.py"; do
  if [ -n "$candidate" ] && [ -f "$candidate" ]; then
    LINTER="$candidate"
    break
  fi
done

if [ -z "$LINTER" ]; then
  echo "Error: tools/lint.py not found." >&2
  echo "  Set UW_SLIDES_HOME or run /uw-slides:new-deck to vendor lint.py into this deck." >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found." >&2
  exit 2
fi

python3 "$LINTER" "$DECK_DIR" "${ARGS[@]}"
