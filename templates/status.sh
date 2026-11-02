#!/bin/bash

# UW Slides Status Script
# Prints a table of every slide: ID, generation state, brief status,
# owner, locked, and layout.
#
# Usage: ./status.sh [deck-dir]
#   deck-dir   path to the deck (default: current directory)
#
# tools/lint.py is found in this order:
#   1. <deck>/tools/lint.py (vendored by /uw-slides:new-deck)
#   2. $UW_SLIDES_HOME/tools/lint.py
#   3. ~/.claude/plugins/local/uw-slides/tools/lint.py

set -e

DECK_DIR="${1:-.}"

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
  echo "  Run /uw-slides:update-deck to add tools/lint.py to this deck, or set UW_SLIDES_HOME." >&2
  exit 2
fi

python3 "$LINTER" "$DECK_DIR" --status
