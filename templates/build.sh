#!/bin/bash

# UW Slides Build Script
# Concatenates HTML fragments into single presentation file

# Usage: ./build.sh [--strict] [deck-dir]
#   --strict  fail (exit 1) if any slide listed in SLIDES.md has no fragment
#
# Slide order comes from SLIDES.md. A heading is a slide only if its text is a
# kebab-case ID (lowercase letters, digits, hyphens), e.g. "## 03-approach" or
# "## approach". Other headings ("## How to render this deck") are ignored.

set -e  # Exit on error

STRICT=0
DECK_DIR="."
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    *) DECK_DIR="$arg" ;;
  esac
done
OUTPUT="$DECK_DIR/build/index.html"

# Create build directory
mkdir -p "$DECK_DIR/build"

echo "Building presentation..."

for required in shared/header.html shared/footer.html SLIDES.md; do
  if [ ! -f "$DECK_DIR/$required" ]; then
    echo "Error: $required not found"
    exit 1
  fi
done

# Slide IDs in SLIDES.md order (CRLF-safe)
slide_ids=$(tr -d '\r' < "$DECK_DIR/SLIDES.md" \
  | sed -n -E 's/^## +([a-z0-9]+(-[a-z0-9]+)*)[[:space:]]*$/\1/p')

if [ -z "$slide_ids" ]; then
  echo "Error: no slide headings found in SLIDES.md (expected lines like '## 01-title')"
  exit 1
fi

duplicates=$(printf '%s\n' "$slide_ids" | sort | uniq -d)
if [ -n "$duplicates" ]; then
  echo "Error: duplicate slide IDs in SLIDES.md:"
  printf '  %s\n' $duplicates
  exit 1
fi

# Assemble in a temp file so a failed build never leaves a partial index.html
TMP_OUTPUT="$OUTPUT.tmp"
trap 'rm -f "$TMP_OUTPUT"' EXIT
cat "$DECK_DIR/shared/header.html" > "$TMP_OUTPUT"

listed_count=0
built_count=0
missing_count=0

while IFS= read -r slide_name; do
  listed_count=$((listed_count + 1))
  slide_file="$DECK_DIR/content/${slide_name}.html"
  if [ -f "$slide_file" ]; then
    cat "$slide_file" >> "$TMP_OUTPUT"
    built_count=$((built_count + 1))
  else
    echo "Warning: content/${slide_name}.html not found (skipping)"
    missing_count=$((missing_count + 1))
  fi
done <<< "$slide_ids"

# Fragments in content/ that SLIDES.md does not list
if [ -d "$DECK_DIR/content" ]; then
  for fragment in "$DECK_DIR"/content/*.html; do
    [ -e "$fragment" ] || continue
    fragment_id=$(basename "$fragment" .html)
    if ! printf '%s\n' "$slide_ids" | grep -qx -- "$fragment_id"; then
      echo "Warning: content/${fragment_id}.html is not listed in SLIDES.md (not included)"
    fi
  done
fi

if [ "$STRICT" -eq 1 ] && [ "$missing_count" -gt 0 ]; then
  echo "Error: $missing_count slide(s) missing (--strict)"
  exit 1
fi

cat "$DECK_DIR/shared/footer.html" >> "$TMP_OUTPUT"
mv "$TMP_OUTPUT" "$OUTPUT"
trap - EXIT

echo "✓ Built $OUTPUT"
echo "  Slides built: $built_count of $listed_count"
