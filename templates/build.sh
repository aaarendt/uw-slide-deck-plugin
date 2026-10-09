#!/bin/bash

# UW Slides Build Script
# Concatenates HTML fragments into single presentation file

# Usage: ./build.sh [--strict] [deck-dir]
#   --strict  fail (exit 1) if any listed slide has no fragment
#
# Slide order comes from deck.yml (the `slides:` list, one ID per line).
# Decks that still have only SLIDES.md build in legacy mode: a heading is a
# slide only if its text is a kebab-case ID (lowercase letters, digits,
# hyphens), e.g. "## 03-approach". That mode is deprecated and will be removed.
#
# deck.yml is read with tools/deckparse.py (python3, standard library only),
# found via $UW_SLIDES_HOME, <deck>/tools/, or ~/.claude/plugins/local/uw-slides.
# Without it the IDs are still read, but deck.yml is not validated.

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

for required in shared/header.html shared/footer.html; do
  if [ ! -f "$DECK_DIR/$required" ]; then
    echo "Error: $required not found"
    exit 1
  fi
done

# Locate tools/deckparse.py (optional)
PARSER=""
for candidate in "${UW_SLIDES_HOME:+$UW_SLIDES_HOME/tools/deckparse.py}" \
                 "$DECK_DIR/tools/deckparse.py" \
                 "$HOME/.claude/plugins/local/uw-slides/tools/deckparse.py"; do
  if [ -n "$candidate" ] && [ -f "$candidate" ]; then
    PARSER="$candidate"
    break
  fi
done

if [ -f "$DECK_DIR/deck.yml" ]; then
  ORDER_SOURCE="deck.yml"
  if [ -n "$PARSER" ] && command -v python3 >/dev/null 2>&1; then
    slide_ids=$(python3 "$PARSER" deck "$DECK_DIR/deck.yml" --format ids) || exit 1
  else
    echo "Warning: deckparse.py or python3 not found; reading deck.yml without validation (set UW_SLIDES_HOME)"
    # Fallback reader: the plain list under a top-level "slides:" key
    slide_ids=$(tr -d '\r' < "$DECK_DIR/deck.yml" | awk -v q="'" '
      BEGIN {
        quote = "[\"" q "]?"
        item = "^[[:space:]]*-[[:space:]]+" quote "[a-z0-9]+(-[a-z0-9]+)*" quote "[[:space:]]*$"
      }
      /^[[:space:]]*#/ { next }
      /^slides:/ { in_slides = ($0 !~ /\[\]/); next }
      /^[^[:space:]-]/ { in_slides = 0 }
      in_slides && $0 ~ item {
        sub("^[[:space:]]*-[[:space:]]+" quote, ""); sub(quote "[[:space:]]*$", ""); print
      }')
  fi
  if [ -f "$DECK_DIR/SLIDES.md" ]; then
    echo "Note: SLIDES.md is ignored because deck.yml exists"
  fi
  if [ -z "$slide_ids" ]; then
    echo "Error: no slides listed in deck.yml (expected a 'slides:' list of IDs)"
    exit 1
  fi
elif [ -f "$DECK_DIR/SLIDES.md" ]; then
  ORDER_SOURCE="SLIDES.md"
  echo "Warning: SLIDES.md is deprecated and support will be removed in v0.3.0."
  echo "         Migrate to deck.yml + slides/ (see references/slide-schema.md, section 6)."
  # Slide IDs in SLIDES.md order (CRLF-safe)
  slide_ids=$(tr -d '\r' < "$DECK_DIR/SLIDES.md" \
    | sed -n -E 's/^## +([a-z0-9]+(-[a-z0-9]+)*)[[:space:]]*$/\1/p')
  if [ -z "$slide_ids" ]; then
    echo "Error: no slide headings found in SLIDES.md (expected lines like '## 01-title')"
    exit 1
  fi
else
  echo "Error: deck.yml not found (or SLIDES.md for a legacy deck)"
  exit 1
fi

duplicates=$(printf '%s\n' "$slide_ids" | sort | uniq -d)
if [ -n "$duplicates" ]; then
  echo "Error: duplicate slide IDs in $ORDER_SOURCE:"
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

# Fragments in content/ that the slide list does not include
if [ -d "$DECK_DIR/content" ]; then
  for fragment in "$DECK_DIR"/content/*.html; do
    [ -e "$fragment" ] || continue
    fragment_id=$(basename "$fragment" .html)
    if ! printf '%s\n' "$slide_ids" | grep -qx -- "$fragment_id"; then
      echo "Warning: content/${fragment_id}.html is not listed in $ORDER_SOURCE (not included)"
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
