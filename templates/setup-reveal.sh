#!/bin/bash

# Download reveal.js assets to assets/reveal/.
#
# Usage: ./setup-reveal.sh [deck-dir]
#
# After running, git-track the files so the deck is offline-capable:
#   git add assets/reveal/
#
# To update to a newer version, change REVEAL_VERSION and re-run.

REVEAL_VERSION="6.0.2"
BASE_URL="https://cdn.jsdelivr.net/npm/reveal.js@${REVEAL_VERSION}/dist"

DECK_DIR="${1:-.}"
TARGET="$DECK_DIR/assets/reveal"

set -e

mkdir -p "$TARGET"

echo "Downloading reveal.js ${REVEAL_VERSION}..."

if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "$TARGET/reveal.min.js"  "$BASE_URL/reveal.min.js"
  curl -fsSL -o "$TARGET/reveal.min.css" "$BASE_URL/reveal.min.css"
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "$TARGET/reveal.min.js"  "$BASE_URL/reveal.min.js"
  wget -q -O "$TARGET/reveal.min.css" "$BASE_URL/reveal.min.css"
else
  echo "Error: curl or wget is required. Download manually:"
  echo "  $BASE_URL/reveal.min.js  → $TARGET/reveal.min.js"
  echo "  $BASE_URL/reveal.min.css → $TARGET/reveal.min.css"
  exit 1
fi

JS_SIZE=$(wc -c < "$TARGET/reveal.min.js")
CSS_SIZE=$(wc -c < "$TARGET/reveal.min.css")
echo "reveal.min.js:  ${JS_SIZE} bytes"
echo "reveal.min.css: ${CSS_SIZE} bytes"
echo ""
echo "Done. Git-track the assets:"
echo "  git add assets/reveal/"
echo ""
echo "Keyboard shortcuts in the browser:"
echo "  Arrow keys / Space  — navigate"
echo "  S                   — presenter view (speaker notes)"
echo "  Esc                 — slide overview"
echo "  ?                   — keyboard help"
echo "  ?print-pdf          — add to URL for print-to-PDF mode"
