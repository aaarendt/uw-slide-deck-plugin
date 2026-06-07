#!/bin/bash

# UW Slides Build Script — Pass 2 (with visuals)
# Concatenates HTML fragments from content-with-visuals/ into a final presentation file.
# Run only after pass 1 (build.sh) and after apply-visuals has been run.

set -e

DECK_DIR="${1:-.}"
OUTPUT="$DECK_DIR/build/index-with-visuals.html"

mkdir -p "$DECK_DIR/build"

echo "Building presentation with visuals..."

if [ ! -f "$DECK_DIR/shared/header.html" ]; then
  echo "Error: shared/header.html not found"
  exit 1
fi

if [ ! -f "$DECK_DIR/SLIDES.md" ]; then
  echo "Error: SLIDES.md not found"
  exit 1
fi

if [ ! -d "$DECK_DIR/content-with-visuals" ]; then
  echo "Error: content-with-visuals/ not found — run apply-visuals first"
  exit 1
fi

cat "$DECK_DIR/shared/header.html" > "$OUTPUT"

slide_count=0

# Use SLIDES.md for ordering; serve fragments from content-with-visuals/ with content/ fallback
grep "^## " "$DECK_DIR/SLIDES.md" | sed 's/^## //' | while IFS= read -r slide_name; do
  [[ -z "$slide_name" ]] && continue

  visuals_file="$DECK_DIR/content-with-visuals/${slide_name}.html"
  content_file="$DECK_DIR/content/${slide_name}.html"

  if [ -f "$visuals_file" ]; then
    cat "$visuals_file" >> "$OUTPUT"
  elif [ -f "$content_file" ]; then
    # Slide not modified by pass 2 — use pass-1 fragment as-is
    cat "$content_file" >> "$OUTPUT"
  else
    echo "Warning: ${slide_name}.html not found in content-with-visuals/ or content/ (skipping)"
  fi
done

slide_count=$(grep -c "^## " "$DECK_DIR/SLIDES.md" || echo 0)

if [ ! -f "$DECK_DIR/shared/footer.html" ]; then
  echo "Error: shared/footer.html not found"
  exit 1
fi

cat "$DECK_DIR/shared/footer.html" >> "$OUTPUT"

echo "✓ Built $OUTPUT"
echo "  Total slides: $slide_count"
