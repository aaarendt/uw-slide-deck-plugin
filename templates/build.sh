#!/bin/bash

# UW Slides Build Script
# Concatenates HTML fragments into single presentation file

set -e  # Exit on error

DECK_DIR="${1:-.}"
OUTPUT="$DECK_DIR/build/index.html"

# Create build directory
mkdir -p "$DECK_DIR/build"

echo "Building presentation..."

# Start with header
if [ ! -f "$DECK_DIR/shared/header.html" ]; then
  echo "Error: shared/header.html not found"
  exit 1
fi

cat "$DECK_DIR/shared/header.html" > "$OUTPUT"

# Add slides in order from SLIDES.md (look for ## slide-id headings)
if [ ! -f "$DECK_DIR/SLIDES.md" ]; then
  echo "Error: SLIDES.md not found"
  exit 1
fi

slide_count=0

# Extract slide IDs from SLIDES.md (lines starting with "## " followed by slide name)
grep "^## " "$DECK_DIR/SLIDES.md" | sed 's/^## //' | while IFS= read -r slide_name; do
  # Skip empty lines
  [[ -z "$slide_name" ]] && continue

  slide_file="$DECK_DIR/content/${slide_name}.html"
  if [ -f "$slide_file" ]; then
    cat "$slide_file" >> "$OUTPUT"
    slide_count=$((slide_count + 1))
  else
    echo "Warning: $slide_file not found (skipping)"
  fi
done

# Count slides for final report (since we're in a subshell with the pipe)
slide_count=$(grep -c "^## " "$DECK_DIR/SLIDES.md" || echo 0)

# Add footer
if [ ! -f "$DECK_DIR/shared/footer.html" ]; then
  echo "Error: shared/footer.html not found"
  exit 1
fi

cat "$DECK_DIR/shared/footer.html" >> "$OUTPUT"

echo "✓ Built $OUTPUT"
echo "  Total slides: $slide_count"
