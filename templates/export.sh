#!/bin/bash

# Export the deck to PDF: one 16:9 page per slide (1920×1080), using
# reveal.js's print mode and Playwright's Chromium.
#
# Prerequisites (optional dependency — not needed to build, present or publish):
#   npm install -g playwright
#   npx playwright install chromium
# (A Playwright installed in the deck folder, npm install playwright, also works.
# If Playwright's Chromium is missing, an installed Google Chrome is used.)
#
# Usage:
#   ./export.sh                   # → build/deck.pdf  (from build/index.html)
#   ./export.sh --visuals         # → build/deck.pdf  (from build/index-with-visuals.html)
#   ./export.sh --notes           # speaker notes printed on a page after each slide
#   ./export.sh [deck-dir]        # run from a different directory
#
# The PDF embeds the fonts the slides use, so it looks the same everywhere.
# They are taken from the deck at export time: the UW brand's Encode Sans from
# assets/fonts/, Open Sans and the CloudBank fonts from Google Fonts (internet
# needed). The script warns when a font could not be loaded, because the PDF
# would then embed a substitute. The PDF is tagged (reading order, alt text).

set -e

DECK_DIR="."
VISUALS=0
NOTES=0
for arg in "$@"; do
  case "$arg" in
    --visuals) VISUALS=1 ;;
    --notes) NOTES=1 ;;
    -*) echo "Error: unknown option $arg (usage: ./export.sh [--visuals] [--notes] [deck-dir])"; exit 2 ;;
    *) DECK_DIR="$arg" ;;
  esac
done

if [ "$VISUALS" -eq 1 ]; then
  if [ -f "$DECK_DIR/build/index-with-visuals.html" ]; then
    INPUT="$DECK_DIR/build/index-with-visuals.html"
  else
    echo "Note: build/index-with-visuals.html not found; exporting build/index.html."
    INPUT="$DECK_DIR/build/index.html"
  fi
else
  INPUT="$DECK_DIR/build/index.html"
fi

if [ ! -f "$INPUT" ]; then
  echo "Error: $INPUT not found. Run ./build.sh first."
  exit 1
fi

OUTPUT="$DECK_DIR/build/deck.pdf"

if ! command -v node >/dev/null 2>&1; then
  echo "Error: Node.js not found. Install Node.js, then: npm install -g playwright && npx playwright install chromium"
  exit 1
fi

echo "Exporting to PDF..."
echo "  Input:  $INPUT"
echo "  Output: $OUTPUT"

# Playwright is found in the deck's node_modules or the global npm folder.
NODE_PATH="$DECK_DIR/node_modules:$(npm root -g 2>/dev/null || true)${NODE_PATH:+:$NODE_PATH}" \
node - "$INPUT" "$OUTPUT" "$NOTES" <<'EOF'
const path = require('path');
const { pathToFileURL } = require('url');

let playwright;
for (const name of ['playwright', 'playwright-core']) {
  try { playwright = require(name); break; } catch (e) { /* try the next */ }
}
if (!playwright) {
  console.error('Error: Playwright not found. Run: npm install -g playwright && npx playwright install chromium');
  process.exit(1);
}

const [input, output, notes] = process.argv.slice(2);
const WIDTH = 1920, HEIGHT = 1080;
const FONT_HOSTS = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;

(async () => {
  let browser;
  try {
    browser = await playwright.chromium.launch();
  } catch (e) {
    try {
      browser = await playwright.chromium.launch({ channel: 'chrome' });
    } catch (e2) {
      console.error('Error: no browser for Playwright. Run: npx playwright install chromium');
      process.exit(1);
    }
  }

  const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });
  const errors = [], fontFailures = new Set();
  page.on('pageerror', e => errors.push(e.message));
  page.on('requestfailed', r => { if (FONT_HOSTS.test(r.url())) fontFailures.add(new URL(r.url()).host); });
  page.on('response', r => { if (FONT_HOSTS.test(r.url()) && r.status() >= 400) fontFailures.add(new URL(r.url()).host); });

  // reveal.js print mode; showNotes=separate-page adds a notes page after each slide.
  const url = pathToFileURL(path.resolve(input)).href + '?print-pdf'
            + (notes === '1' ? '&showNotes=separate-page' : '');
  await page.goto(url, { waitUntil: 'load' });

  const reveal = await page.waitForFunction(
    () => window.Reveal && Reveal.isReady && Reveal.isReady() && document.querySelector('.pdf-page'),
    null, { timeout: 20000 }).then(() => true, () => false);
  if (!reveal) {
    console.warn('  Warning: reveal.js did not start, so the PDF may hold only the first slide.');
    console.warn('           Check that assets/reveal/ exists (./setup-reveal.sh).');
  }
  await page.evaluate(() => document.fonts.ready);
  await page.waitForLoadState('networkidle').catch(() => {});

  const failedFaces = await page.evaluate(() =>
    [...document.fonts].filter(f => f.status === 'error').map(f => `${f.family.replace(/"/g, '')} ${f.weight}`));
  if (failedFaces.length) {
    console.warn(`  Warning: ${failedFaces.length} font file(s) failed to load and were replaced in the PDF: `
      + [...new Set(failedFaces)].slice(0, 5).join(', ') + (failedFaces.length > 5 ? ', ...' : ''));
    console.warn('           Check assets/fonts/ (UW decks).');
  }
  if (fontFailures.size) {
    console.warn(`  Warning: could not reach ${[...fontFailures].join(', ')}; web fonts (Open Sans, CloudBank fonts)`);
    console.warn('           were replaced in the PDF. Export again with internet access.');
  }
  for (const e of errors) console.warn(`  Warning: page error: ${e}`);

  // No page break after the last page (reveal adds one, which leaves a blank
  // page at the end in notes mode).
  await page.addStyleTag({ content: '.reveal .slides > :last-child { break-after: auto !important; page-break-after: auto !important; }' });

  await page.pdf({
    path: output,
    width: `${WIDTH}px`,
    height: `${HEIGHT}px`,
    printBackground: true,
    tagged: true,
  });
  const pages = await page.evaluate(() => document.querySelectorAll('.pdf-page').length);
  await browser.close();
  console.log(`  Slides: ${pages || 'unknown'}`);
})().catch(e => { console.error(`Error: ${e.message}`); process.exit(1); });
EOF

echo "Done: $OUTPUT"
