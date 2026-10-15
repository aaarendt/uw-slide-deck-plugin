#!/bin/bash

# Export presentation to PDF using reveal.js's print-to-PDF mode and Playwright.
#
# Prerequisites (optional dependency — not required to build or present):
#   npm install -g playwright
#   npx playwright install chromium
#
# Usage:
#   ./export.sh                   # → build/deck.pdf  (from build/index.html)
#   ./export.sh --visuals         # → build/deck.pdf  (from build/index-with-visuals.html)
#   ./export.sh [deck-dir]        # run from a different directory
#
# Output: one PDF page per slide, landscape, A4 (matches 16:9 aspect ratio well).
# For pixel-exact PNG snapshots, change --format pdf to --format png in the script
# and set --full-page.

set -e

DECK_DIR="."
VISUALS=0
for arg in "$@"; do
  case "$arg" in
    --visuals) VISUALS=1 ;;
    *) DECK_DIR="$arg" ;;
  esac
done

if [ "$VISUALS" -eq 1 ] && [ -f "$DECK_DIR/build/index-with-visuals.html" ]; then
  INPUT="$DECK_DIR/build/index-with-visuals.html"
else
  INPUT="$DECK_DIR/build/index.html"
fi

OUTPUT="$DECK_DIR/build/deck.pdf"

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx not found. Install Node.js and run: npm install -g playwright"
  exit 1
fi

# reveal.js print-to-PDF mode: append ?print-pdf to the URL before printing.
ABS_INPUT="file://$(realpath "$INPUT")?print-pdf"

echo "Exporting to PDF..."
echo "  Input:  $INPUT"
echo "  Output: $OUTPUT"

npx playwright pdf \
  --wait-for-load-state networkidle \
  --landscape \
  --format A4 \
  "$ABS_INPUT" "$OUTPUT"

echo "Done: $OUTPUT"
