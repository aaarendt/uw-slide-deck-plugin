# Runtime Evaluation: reveal.js vs. Homegrown Navigation

**Decision: Adopt reveal.js 6.0.2** (MIT, ~169 KB combined JS+CSS).

---

## Comparison

| Feature | Homegrown footer.html | reveal.js 6.0.2 |
|---|---|---|
| Keyboard nav (arrows, space, Page Up/Down, Home/End) | ✓ | ✓ |
| Touch / swipe | — | ✓ |
| Hash-based URL routing | ✓ | ✓ |
| Slide counter | ✓ (custom) | ✓ (`slideNumber: true`) |
| aria-live slide change announcements | ✓ (custom) | ✓ (built-in) |
| Presenter view with speaker notes | — | ✓ (press S) |
| Slide overview | — | ✓ (press Esc) |
| Print to PDF | — | ✓ (`?print-pdf` query param + browser print) |
| Fragment/step reveals | — | ✓ |
| Offline (no CDN) | ✓ | ✓ (with vendored assets) |
| Licence | — | MIT |
| Added size | 0 KB | ~169 KB |

## Recommendation: adopt

The homegrown footer handles navigation correctly but has no presenter view, no overview mode, no PDF export, and no speaker notes. All four are explicitly requested features. reveal.js provides them free of additional code and is MIT-licensed, offline-capable, and well-maintained.

**Migration cost is low.** Existing `<section class="slide">` fragments require no edits. Only the `shared/header.html` and `shared/footer.html` managed files change.

## Compatibility analysis

### Fragment markup: no changes required

reveal.js expects `<section>` elements inside `.reveal > .slides`. Our fragments already use `<section data-slide="..." class="slide">` with inline scoped `<style>` tags. reveal.js does not touch the content inside sections; it only adds `aria-hidden`, display transforms, and `class="past/present/future"` on the section elements themselves. Scoped selectors like `section[data-slide="03-approach"] { ... }` continue to work.

### vw-based font sizes

Our layout library uses `clamp(1.5rem, 2vw, 2rem)` throughout. `vw` references the browser viewport width, not the slide canvas. reveal.js is configured with `width: '100%', height: '100%'` (see footer configuration below) so the reveal container fills the viewport — no CSS-transform scaling is applied. This means `vw` units behave identically to the homegrown layout and no font-size changes are needed in existing slides.

If a future project switches to a fixed-canvas mode (`width: 1280, height: 720`) for aspect-ratio locking, `vw`-based sizes would need to change to `em`/`rem`. Document this in the slide brief schema if that mode is adopted.

### `.active` class removal

The homegrown footer used `section.slide.active { display: flex }` to show the current slide and `display: none` to hide others. reveal.js uses CSS transforms and `visibility`/`opacity` instead. The reveal header removes the `display: none` / `.active` rules and lets reveal.js manage visibility.

### Speaker notes

Slide briefs have a `## Notes` section. generate-slides renders these as `<aside class="notes">` inside the `<section>`. reveal.js's presenter view (S key) shows the notes alongside a slide preview and a timer. Notes are never rendered in the main presentation view.

## Migration for existing decks

Existing decks (built before WS8) have the legacy `footer.html` and `header.html`. Migrate them with `/uw-slides:update-deck`:

1. Run `/uw-slides:update-deck` — it diffs and updates `shared/header.html`, `shared/footer.html`.
2. Download reveal.js: `./setup-reveal.sh` (written to the deck by `update-deck`).
3. Run `./build.sh` and test.
4. Regenerate slides that need `<aside class="notes">` populated from their briefs.

## Vendoring reveal.js

New decks scaffold reveal.js automatically (see new-deck skill, step 12). The assets live at:

```
<deck>/
└── assets/
    └── reveal/
        ├── reveal.min.js   (119 KB, reveal.js 6.0.2)
        └── reveal.min.css  (54 KB, reveal.js 6.0.2)
```

Source: `https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/dist/`

To vendor manually or update to a new version:

```bash
cd <deck>
curl -o assets/reveal/reveal.min.js \
  https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/dist/reveal.min.js
curl -o assets/reveal/reveal.min.css \
  https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/dist/reveal.min.css
```

Git-track the vendored files so the deck is fully self-contained and reproducible offline.

## reveal.js configuration

```js
Reveal.initialize({
  hash: true,                  // URL reflects current slide (#/3)
  width: '100%',               // Fill viewport (preserves vw-based font sizes)
  height: '100%',              // Fill viewport
  margin: 0,                   // No padding around slides
  minScale: 1,                 // Disable scale-down
  maxScale: 1,                 // Disable scale-up
  transition: 'none',          // Instant transitions; change to 'fade' or 'slide' if desired
  slideNumber: 'c/t',          // "current / total" counter
  controls: false,             // No click arrows (keyboard/touch sufficient)
  progress: false,             // No progress bar (slide counter is enough)
  center: false,               // Slides fill canvas; no vertical centering
  keyboard: true,
  touch: true,
  help: true,                  // ? key shows keyboard help
});
```

## PDF export

Print to PDF using the browser's built-in print dialog with the `?print-pdf` query parameter:

```
open "build/index.html?print-pdf"
# Then File → Print → Save as PDF
# In Chrome/Chromium: set paper to Landscape, no margins, background graphics on
```

For automated export see `templates/export.sh` (requires Playwright and Node).

## Decisions open after WS8

- **O3 (PPTX)**: HTML + PDF (above) covers most use cases. PPTX remains deferred.
- **O4 (Fonts)**: Copying 9 MB of Encode Sans per deck is unchanged. Font subsetting (e.g., `pyftsubset`) can reduce this to ~500 KB for the weights actually used; track as a separate task.
