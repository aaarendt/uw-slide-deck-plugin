#!/bin/bash

# Produces build/index-published.html: one file with the deck's images,
# reveal.js stylesheet, reveal.js script and speaker-notes plugin inlined,
# so it works on its own (emailed, uploaded, or served from build/ alone).
#
# Usage: ./publish.sh [--site] [deck-dir]
#   --site  also write build/site/, ready to upload as a web site (GitHub
#           Pages): index.html plus the local files it still links to (the
#           UW brand's fonts), copied with their paths fixed for the site.
#
# Input: build/index-with-visuals.html (./build-visuals.sh). If that file is
# missing, build/index.html (./build.sh) is published instead.
#
# What stays a link: fonts. Local font files (UW brand, assets/fonts/) load
# only where they sit next to the file, as they do in build/site/; web fonts
# (Google Fonts) need internet access. The script lists these at the end.
#
# Requires python3 (standard library only).

set -e

DECK_DIR="."
SITE=0
for arg in "$@"; do
  case "$arg" in
    --site) SITE=1 ;;
    -*) echo "Error: unknown option $arg (usage: ./publish.sh [--site] [deck-dir])"; exit 2 ;;
    *) DECK_DIR="$arg" ;;
  esac
done

BUILD_DIR="$DECK_DIR/build"
OUTPUT="$BUILD_DIR/index-published.html"
SITE_DIR=""
[ "$SITE" -eq 1 ] && SITE_DIR="$BUILD_DIR/site"

if [ -f "$BUILD_DIR/index-with-visuals.html" ]; then
  INPUT="$BUILD_DIR/index-with-visuals.html"
  if [ -f "$BUILD_DIR/index.html" ] && [ "$BUILD_DIR/index.html" -nt "$INPUT" ]; then
    echo "Warning: build/index.html is newer than build/index-with-visuals.html."
    echo "         Run ./build-visuals.sh first to publish the latest content."
  fi
elif [ -f "$BUILD_DIR/index.html" ]; then
  INPUT="$BUILD_DIR/index.html"
  echo "Note: build/index-with-visuals.html not found; publishing build/index.html."
  echo "      Run ./build-visuals.sh first if the deck has pass-2 visuals."
else
  echo "Error: no build found in $BUILD_DIR. Run ./build.sh (and ./build-visuals.sh) first."
  exit 1
fi

echo "Inlining assets from $(basename "$INPUT")..."

python3 - "$BUILD_DIR" "$INPUT" "$OUTPUT" "$SITE_DIR" <<'EOF'
import sys, re, base64, os, shutil
from urllib.parse import urlsplit

build_dir, input_path, output_path, site_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

with open(input_path, 'r', encoding='utf-8') as f:
    html = f.read()


def is_external(path):
    """URLs left alone: web addresses, data: URIs, in-page anchors."""
    p = path.strip().lower()
    return (p.startswith(('http:', 'https:', '//', 'data:', '#', 'mailto:', 'tel:', 'javascript:'))
            or p == '')


def local_file(path):
    """Absolute path of a local reference, resolved like the browser does from build/."""
    clean = path.split('#', 1)[0].split('?', 1)[0]
    return os.path.normpath(os.path.join(build_dir, clean))


def read_text(path):
    """Contents of a local text asset, or None (with a warning) if unusable."""
    abs_path = local_file(path)
    if not os.path.isfile(abs_path):
        print(f'  Warning: not found — {path}')
        return None
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        print(f'  Warning: not UTF-8, left as a link — {path}')
        return None
    return text.lstrip('﻿')


def attr(tag, name):
    m = re.search(r'\b' + name + r'\s*=\s*(["\'])(.*?)\1', tag, re.I | re.S)
    return m.group(2) if m else None


# --- 1. Images: src="..." -> data: URI --------------------------------------
# Runs on the page as built, before any script or stylesheet text is inlined,
# so it never rewrites strings inside reveal.js. Script sources (.js) are left
# for step 2.

def mime(ext):
    return {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'gif': 'image/gif', 'svg': 'image/svg+xml', 'webp': 'image/webp'}.get(ext.lower())


def replace_src(match):
    path = match.group(1)
    if is_external(path):
        return match.group(0)
    abs_path = local_file(path)
    ext = abs_path.rsplit('.', 1)[-1] if '.' in os.path.basename(abs_path) else ''
    if ext.lower() in ('js', 'mjs'):
        return match.group(0)  # inlined in step 2
    if not os.path.isfile(abs_path):
        print(f'  Warning: not found — {path}')
        return match.group(0)
    m = mime(ext)
    if not m:
        print(f'  Warning: unknown type — {path}')
        return match.group(0)
    with open(abs_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    print(f'  Inlined: {path}')
    return f'src="data:{m};base64,{b64}"'


html = re.sub(r'src="([^"]+)"', replace_src, html)


# --- 2. Stylesheets and scripts -> inline <style> / <script> ----------------
# Callables only: the replacement text contains backslashes (reveal.js does),
# which a replacement string would reinterpret.

def guard_end_tag(text, tag):
    """Stop '</script' or '</style' inside the asset from closing the element early."""
    return re.sub(r'</(' + tag + r')', lambda m: '<\\/' + m.group(1), text, flags=re.I)


def risky_comment(js):
    """'<!--' followed by '<script' with no '-->' between keeps an inline script open."""
    for m in re.finditer(r'<!--', js):
        rest = js[m.end():]
        close = rest.find('-->')
        if re.search(r'<script[\s/>]', rest if close < 0 else rest[:close], re.I):
            return True
    return False


def inline_stylesheet(match):
    tag = match.group(0)
    rel = (attr(tag, 'rel') or '').lower().split()
    href = attr(tag, 'href')
    if 'stylesheet' not in rel or not href or is_external(href):
        return tag
    css = read_text(href)
    if css is None:
        return tag
    for url in re.findall(r'url\(\s*["\']?([^"\')]+)', css):
        if not is_external(url):
            print(f'  Warning: {href} refers to {url}, which is relative to the stylesheet and will not load')
    media = attr(tag, 'media')
    open_tag = f'<style media="{media}">' if media and media.lower() != 'all' else '<style>'
    print(f'  Inlined: {href}')
    return f'{open_tag}\n{guard_end_tag(css, "style")}\n</style>'


def inline_script(match):
    attrs, src = match.group(1) + match.group(3), match.group(2)
    if is_external(src):
        return match.group(0)
    js = read_text(src)
    if js is None:
        return match.group(0)
    if risky_comment(js):
        print(f'  Warning: {src} contains "<!--" followed by "<script"; check the published deck loads')
    # src, defer and async have no meaning on an inline script.
    attrs = re.sub(r'\s+(defer|async)\b(\s*=\s*(["\']).*?\3)?', '', attrs, flags=re.I)
    print(f'  Inlined: {src}')
    return f'<script{attrs}>\n{guard_end_tag(js, "script")}\n</script>'


html = re.sub(r'<link\b[^>]*>', inline_stylesheet, html, flags=re.I)
html = re.sub(r'<script\b([^>]*?)\s+src\s*=\s*"([^"]+)"([^>]*)>\s*</script\s*>',
              inline_script, html, flags=re.I)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)


# --- 3. Report what the published file still depends on ---------------------
# Scans the page with inlined <script>/<style> text blanked out, so strings
# inside reveal.js are not mistaken for references. Inline <style> blocks from
# the deck itself (the brand header's @font-face rules) are scanned.

def blank_inlined(text):
    def blank(m):
        return m.group(1) + m.group(3)
    text = re.sub(r'(<script\b[^>]*>)(.*?)(</script\s*>)', blank, text, flags=re.I | re.S)
    return text


scan = blank_inlined(html)
local, remote = {}, set()

for m in re.finditer(r'\b(?:src|href)\s*=\s*"([^"]+)"', scan):
    tag_start = scan.rfind('<', 0, m.start())
    tag_name = re.match(r'<\s*(\w+)', scan[tag_start:])
    tag_name = tag_name.group(1).lower() if tag_name else ''
    ref = m.group(1)
    if tag_name == 'a':
        continue  # hyperlinks are navigation, not part of the page
    if is_external(ref):
        if ref.lower().startswith(('http:', 'https:', '//')):
            remote.add(urlsplit(ref if not ref.startswith('//') else 'https:' + ref).netloc)
        continue
    local.setdefault(os.path.dirname(ref) or '.', set()).add(ref)

for m in re.finditer(r'url\(\s*["\']?([^"\')]+)', scan):
    ref = m.group(1).strip()
    if ref.lower().startswith(('http:', 'https:', '//')):
        remote.add(urlsplit(ref if not ref.startswith('//') else 'https:' + ref).netloc)
    elif not is_external(ref):
        local.setdefault(os.path.dirname(ref) or '.', set()).add(ref)

if local:
    total = sum(len(v) for v in local.values())
    print(f'  Not inlined: {total} local file(s); the published file needs them next to it:')
    for folder in sorted(local):
        refs = sorted(local[folder])
        sample = os.path.basename(refs[0])
        more = f' and {len(refs) - 1} more' if len(refs) > 1 else ''
        print(f'    {folder}/  ({sample}{more})')
if remote:
    print(f'  Needs internet for: {", ".join(sorted(remote))}')

size_kb = os.path.getsize(output_path) / 1024
print(f'  Size: {size_kb:,.0f} KB')


# --- 4. Optional web site: build/site/ ---------------------------------------
# index.html is the published page with each remaining local reference
# rewritten from build/-relative ("../assets/fonts/X.ttf") to site-relative
# ("assets/fonts/X.ttf"), and the referenced files copied to the same place.
# Relative paths keep working when the site is served from a subfolder, as a
# GitHub Pages project site is (https://<user>.github.io/<repo>/).

def outside_scripts(text, fn):
    """Apply fn to the parts of text that are not <script> elements."""
    parts = re.split(r'(<script\b[^>]*>.*?</script\s*>)', text, flags=re.I | re.S)
    return ''.join(p if i % 2 else fn(p) for i, p in enumerate(parts))


if site_dir:
    deck_root = os.path.dirname(os.path.abspath(build_dir))
    if os.path.isdir(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir)

    mapping, copied, problems = {}, 0, 0
    for ref in sorted({r for refs in local.values() for r in refs}):
        abs_path = os.path.abspath(local_file(ref))
        rel = os.path.relpath(abs_path, deck_root)
        if rel == os.pardir or rel.startswith(os.pardir + os.sep):
            print(f'  Warning: {ref} is outside the deck folder; not copied to the site')
            problems += 1
            continue
        if not os.path.isfile(abs_path):
            print(f'  Warning: not found — {ref}; not copied to the site')
            problems += 1
            continue
        dest = os.path.join(site_dir, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(abs_path, dest)
        copied += 1
        suffix = ref[len(ref.split('#', 1)[0].split('?', 1)[0]):]  # keep ?query / #fragment
        mapping[ref] = rel.replace(os.sep, '/') + suffix

    def rewrite(text):
        # Longest first, bounded by a quote, paren or space, so one reference
        # never rewrites part of another.
        for ref in sorted(mapping, key=len, reverse=True):
            text = re.sub(r'(?<=["\'(\s])' + re.escape(ref) + r'(?=["\')\s])',
                          lambda m, new=mapping[ref]: new, text)
        return text

    with open(os.path.join(site_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(outside_scripts(html, rewrite))
    print(f'  Site: {site_dir}/index.html + {copied} linked file(s)'
          + (f', {problems} missing' if problems else ''))
EOF

echo "✓ Published: $OUTPUT"
[ "$SITE" -eq 1 ] && echo "✓ Site: $SITE_DIR/ (upload this folder; index.html is the deck)"
exit 0
