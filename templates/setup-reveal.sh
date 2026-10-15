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
DIST_URL="https://cdn.jsdelivr.net/npm/reveal.js@${REVEAL_VERSION}/dist"
PLUGIN_URL="https://cdn.jsdelivr.net/npm/reveal.js@${REVEAL_VERSION}/plugin/notes"

DECK_DIR="${1:-.}"
TARGET="$DECK_DIR/assets/reveal"

set -e

mkdir -p "$TARGET/plugin/notes"

echo "Downloading reveal.js ${REVEAL_VERSION}..."

if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "$TARGET/reveal.min.js"           "$DIST_URL/reveal.min.js"
  curl -fsSL -o "$TARGET/reveal.min.css"          "$DIST_URL/reveal.min.css"
  curl -fsSL -o "$TARGET/plugin/notes/notes.js"   "$PLUGIN_URL/notes.js"
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "$TARGET/reveal.min.js"           "$DIST_URL/reveal.min.js"
  wget -q -O "$TARGET/reveal.min.css"          "$DIST_URL/reveal.min.css"
  wget -q -O "$TARGET/plugin/notes/notes.js"   "$PLUGIN_URL/notes.js"
else
  echo "Error: curl or wget is required. Download manually:"
  echo "  $DIST_URL/reveal.min.js                → $TARGET/reveal.min.js"
  echo "  $DIST_URL/reveal.min.css               → $TARGET/reveal.min.css"
  echo "  $PLUGIN_URL/notes.js                   → $TARGET/plugin/notes/notes.js"
  exit 1
fi

JS_SIZE=$(wc -c < "$TARGET/reveal.min.js")
CSS_SIZE=$(wc -c < "$TARGET/reveal.min.css")
NOTES_SIZE=$(wc -c < "$TARGET/plugin/notes/notes.js")
echo "reveal.min.js:          ${JS_SIZE} bytes"
echo "reveal.min.css:         ${CSS_SIZE} bytes"
echo "plugin/notes/notes.js:  ${NOTES_SIZE} bytes"
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
