#!/bin/bash

# UW Slides Outline Script
# Regenerates OUTLINE.md, a read-only overview (ID, key message, layout,
# minutes, owner, status, objectives) from deck.yml and slides/*.md.
# OUTLINE.md is generated: never edit it by hand.
#
# Usage: ./outline.sh [deck-dir]
#
# Needs python3 and tools/deckparse.py, found via $UW_SLIDES_HOME,
# <deck>/tools/, or ~/.claude/plugins/local/uw-slides.

set -e

DECK_DIR="${1:-.}"

if [ ! -f "$DECK_DIR/deck.yml" ]; then
  echo "Error: deck.yml not found in $DECK_DIR (OUTLINE.md is generated from deck.yml and slides/)"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required"
  exit 1
fi

PARSER=""
for candidate in "${UW_SLIDES_HOME:+$UW_SLIDES_HOME/tools/deckparse.py}" \
                 "$DECK_DIR/tools/deckparse.py" \
                 "$HOME/.claude/plugins/local/uw-slides/tools/deckparse.py"; do
  if [ -n "$candidate" ] && [ -f "$candidate" ]; then
    PARSER="$candidate"
    break
  fi
done

if [ -z "$PARSER" ]; then
  echo "Error: tools/deckparse.py not found (set UW_SLIDES_HOME to the plugin directory)"
  exit 1
fi

# Write via a temp file so a failed run never truncates OUTLINE.md
TMP_OUTPUT="$DECK_DIR/OUTLINE.md.tmp"
trap 'rm -f "$TMP_OUTPUT"' EXIT
python3 "$PARSER" outline "$DECK_DIR" > "$TMP_OUTPUT"
mv "$TMP_OUTPUT" "$DECK_DIR/OUTLINE.md"
trap - EXIT

echo "✓ Wrote $DECK_DIR/OUTLINE.md"
