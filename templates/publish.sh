#!/bin/bash

# Produces a self-contained index-published.html with all images inlined as base64.

set -e

DECK_DIR="${1:-.}"
INPUT="$DECK_DIR/build/index-with-visuals.html"
OUTPUT="$DECK_DIR/build/index-published.html"

if [ ! -f "$INPUT" ]; then
  echo "Error: $INPUT not found. Run build-visuals.sh first."
  exit 1
fi

echo "Inlining images..."

python3 - "$DECK_DIR/build" "$INPUT" "$OUTPUT" <<'EOF'
import sys, re, base64, os

build_dir, input_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

with open(input_path, 'r', encoding='utf-8') as f:
    html = f.read()

def mime(ext):
    return {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'gif': 'image/gif', 'svg': 'image/svg+xml', 'webp': 'image/webp'}.get(ext.lower())

def replace_src(match):
    path = match.group(1)
    if path.startswith('http') or path.startswith('data:'):
        return match.group(0)
    abs_path = os.path.normpath(os.path.join(build_dir, path))
    if not os.path.isfile(abs_path):
        print(f'  Warning: not found — {path}')
        return match.group(0)
    ext = abs_path.rsplit('.', 1)[-1]
    m = mime(ext)
    if not m:
        print(f'  Warning: unknown type — {path}')
        return match.group(0)
    with open(abs_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    print(f'  Inlined: {path}')
    return f'src="data:{m};base64,{b64}"'

html = re.sub(r'src="([^"]+)"', replace_src, html)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
EOF

echo "✓ Published: $OUTPUT"
