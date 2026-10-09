#!/bin/bash

# UW Slides Build Script — Pass 2 (with visuals)
# Concatenates HTML fragments from content-with-visuals/ into a final presentation file.
# Run only after pass 1 (build.sh) and after apply-visuals has been run.
#
# Usage: ./build-visuals.sh [--strict] [deck-dir]
#   --strict  fail (exit 1) if any slide listed in SLIDES.md has no fragment
#
# Slide IDs follow the same rule as build.sh: a "## " heading whose text is a
# kebab-case ID (lowercase letters, digits, hyphens).

set -e

STRICT=0
DECK_DIR="."
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    *) DECK_DIR="$arg" ;;
  esac
done
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

if [ ! -f "$DECK_DIR/shared/footer.html" ]; then
  echo "Error: shared/footer.html not found"
  exit 1
fi

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

# Assemble in a temp file so a failed build never leaves a partial output
TMP_OUTPUT="$OUTPUT.tmp"
trap 'rm -f "$TMP_OUTPUT"' EXIT
cat "$DECK_DIR/shared/header.html" > "$TMP_OUTPUT"

listed_count=0
built_count=0
missing_count=0

# Serve fragments from content-with-visuals/ with content/ fallback
while IFS= read -r slide_name; do
  listed_count=$((listed_count + 1))

  visuals_file="$DECK_DIR/content-with-visuals/${slide_name}.html"
  content_file="$DECK_DIR/content/${slide_name}.html"

  if [ -f "$visuals_file" ]; then
    cat "$visuals_file" >> "$TMP_OUTPUT"
    built_count=$((built_count + 1))
  elif [ -f "$content_file" ]; then
    # Slide not modified by pass 2 — use pass-1 fragment as-is
    cat "$content_file" >> "$TMP_OUTPUT"
    built_count=$((built_count + 1))
  else
    echo "Warning: ${slide_name}.html not found in content-with-visuals/ or content/ (skipping)"
    missing_count=$((missing_count + 1))
  fi
done <<< "$slide_ids"

# Fragments in either directory that SLIDES.md does not list
for dir in content content-with-visuals; do
  [ -d "$DECK_DIR/$dir" ] || continue
  for fragment in "$DECK_DIR/$dir"/*.html; do
    [ -e "$fragment" ] || continue
    fragment_id=$(basename "$fragment" .html)
    if ! printf '%s\n' "$slide_ids" | grep -qx -- "$fragment_id"; then
      echo "Warning: ${dir}/${fragment_id}.html is not listed in SLIDES.md (not included)"
    fi
  done
done

if [ "$STRICT" -eq 1 ] && [ "$missing_count" -gt 0 ]; then
  echo "Error: $missing_count slide(s) missing (--strict)"
  exit 1
fi

cat "$DECK_DIR/shared/footer.html" >> "$TMP_OUTPUT"
mv "$TMP_OUTPUT" "$OUTPUT"
trap - EXIT

echo "✓ Built $OUTPUT"
echo "  Slides built: $built_count of $listed_count"
