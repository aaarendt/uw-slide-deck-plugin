# UW Slides Plugin

Create branded presentations with any LLM using a fragment-based architecture. Ships with University of Washington and CloudBank themes; extensible to additional brands.

## Features

- **LLM-friendly:** Slides, briefs and the design docs are plain files any LLM can read and write. The skills and install steps below target Claude Code; with other tools, point the LLM at `AGENTS.md` and the design docs instead
- **Fragment-based:** Each slide is self-contained HTML with inline scoped styles
- **Two-pass workflow:** Pass 1 builds content and layout; pass 2 adds visuals
- **Brief-driven:** `deck.yml` holds the slide order; one brief per slide (`slides/<id>.md`) holds the message, layout, notes, owner and status. The HTML is generated from the briefs and can be regenerated safely (locked slides are never overwritten)
- **UW brand compliant:** Design system documented in `design-systems/uw-brand/DESIGN.md`
- **WCAG 2.1 AA accessible:** Built-in accessibility requirements
- **Simple build:** Bash scripts; `python3` (standard library only, no pip) powers `tools/deckparse.py` (validation, slide status, `OUTLINE.md`) and `publish.sh`. Builds still work without it, with the slide list read unvalidated
- **Schema:** `deck.yml` and the briefs are defined in `references/slide-schema.md`. `SLIDES.md` (legacy) still builds, with a deprecation warning
- **Layout library:** 12 brand-neutral slide layouts (`templates/layouts/`, documented in `references/layouts.md`) that render in both the UW and CloudBank brands

---

## Installation

```bash
ln -s /path/to/uw-slides-plugin ~/.claude/plugins/local/uw-slides
```

No other dependencies. The plugin is now available in any Claude Code session.

---

## Quick Start

```bash
# Scaffold a new presentation
/uw-slides:new-deck my-presentation

# Plan your deck from a topic (writes deck.yml and slides/*.md, stops for your approval):
cd my-presentation
/uw-slides:plan-deck "Cloud computing for researchers" --duration=45

# After approving the plan, generate the slides:
/uw-slides:generate-slides

# Download the reveal.js runtime (once per deck):
./setup-reveal.sh

# Build and preview
./build.sh
open build/index.html
```

---

## How It Works

### Directory Structure

```
presentation-name/
├── shared/
│   ├── header.html            # Design tokens, fonts, base styles
│   └── footer.html            # reveal.js initialisation, closing tags
├── content/                   # Pass-1 slide fragments (text, layout, color)
├── content-with-visuals/      # Pass-2 slide fragments (adds photos, diagrams)
├── assets/
│   ├── images/
│   ├── diagrams/
│   └── reveal/                # reveal.js runtime (downloaded by setup-reveal.sh)
├── tools/
│   └── deckparse.py           # Vendored parser/validator (stdlib only)
├── .uw-slides.json            # Plugin version stamp and brand
├── deck.yml                   # Deck metadata, objectives and slide order
├── slides/                    # One brief per slide (slides/<id>.md)
├── OUTLINE.md                 # Generated read-only overview (./outline.sh)
├── VISUALS.md                 # Pass-2 additions spec — photos, diagrams, icons
├── build.sh                   # Pass-1 build: content/ → build/index.html
├── build-visuals.sh           # Pass-2 build: content-with-visuals/ → build/index-with-visuals.html
├── outline.sh                 # Regenerates OUTLINE.md
├── setup-reveal.sh            # Downloads reveal.js assets (run once after scaffold)
├── export.sh                  # PDF export via Playwright (optional)
└── publish.sh                 # Pass-3: inline images into one portable file
```

### deck.yml and the Briefs Are the Source of Truth

`deck.yml` lists the slides in order; the build script concatenates `content/<id>.html` in that order, so moving a line reorders the built presentation. Each slide has a brief, `slides/<id>.md`: a short front matter block (layout, owner, status, duration, `locked`) and sections for the key message, talking points, source and speaker notes. Format and rules: `references/slide-schema.md`.

A slide ID is lowercase letters, digits and single hyphens (`03-approach`). IDs must be unique, and each needs a brief and, once generated, a fragment `content/<id>.html`.

`content/*.html` is generated from the briefs and records which version of the brief it came from (`data-brief-hash`). `/uw-slides:generate-slides` skips slides with `locked: true` (hand-edited HTML) and asks before replacing a slide whose brief changed. To check the state of every slide: `python3 tools/deckparse.py status <deck-dir>`. `./outline.sh` writes `OUTLINE.md`, a generated overview that is never edited by hand.

**Legacy decks** with only a `SLIDES.md` still build (headings `## <kebab-case-id>` give the order) and print a deprecation warning; the fallback is planned for removal in v0.3.0. See [Migrating from SLIDES.md](#migrating-from-slidesmd) below.

### Fragment Pattern

Each slide is a complete HTML `<section>` saved as `content/<slide-id>.html`:

```html
<section data-slide="03-approach"
         aria-label="Slide 3: Our Approach"
         class="slide">

  <div class="content">
    <h1>Our Approach</h1>
    <p>Content goes here...</p>
  </div>

  <style>
    section[data-slide="03-approach"] {
      background: var(--uw-spirit-purple);
      padding: var(--space-20);
    }
    section[data-slide="03-approach"] h1 {
      font-family: var(--font-display);
      color: var(--uw-spirit-gold);
    }
  </style>
</section>
```

The `section[data-slide="..."]` selector scopes all styles to that slide — no class name collisions, no cascade issues.

### Build Process

```bash
./build.sh            # Pass 1 → build/index.html
./build-visuals.sh    # Pass 2 → build/index-with-visuals.html
```

Both scripts accept an optional path argument: `./build.sh /path/to/deck`

By default a slide listed in `deck.yml` with no fragment yet is skipped with a warning, so you can build while the deck is in progress. Use `--strict` (`./build.sh --strict`) to fail instead, for example in CI. An invalid `deck.yml` (such as a duplicate ID) always fails the build, and fragments in `content/` that `deck.yml` doesn't list are reported as warnings.

The scripts read `deck.yml` with `tools/deckparse.py` (needs `python3`). New decks ship a vendored copy in `<deck>/tools/deckparse.py` (put there by `/uw-slides:new-deck`); the scripts also check `$UW_SLIDES_HOME/tools/` and `~/.claude/plugins/local/uw-slides/tools/` as fallbacks. If none is found they still read the plain `slides:` list, without validation.

### Two-Pass Workflow

**Pass 1 — content and structure:**
1. Run `/uw-slides:plan-deck` (or edit `deck.yml` and the briefs in `slides/` by hand). The planner drafts learning objectives, picks a layout per slide, fills the slots and stops for your approval before any HTML is written. Run it again later to add, remove, merge or split slides or to change the length; it leaves locked, owned and `done` slides alone
2. Run `/uw-slides:generate-slides` → `content/*.html` fragments
3. Run `./build.sh` → `build/index.html`
4. The deck should look complete at this stage — no image placeholders

**Pass 2 — visual additions:**
1. Specify photographs, diagrams, and icons in `VISUALS.md`
2. Run `/uw-slides:apply-visuals` → writes to `content-with-visuals/`
3. Run `./build-visuals.sh` → `build/index-with-visuals.html`

Pass 2 is additive. Slides not listed in VISUALS.md are served unchanged from `content/`. Pass 2 never modifies pass-1 files.

### Runtime (reveal.js)

New decks use [reveal.js](https://revealjs.com/) 6.0.2 as the presentation runtime. Run `setup-reveal.sh` once after scaffolding to download the assets:

```bash
./setup-reveal.sh        # downloads assets/reveal/ (reveal.min.js, reveal.min.css, plugin/notes/notes.js)
git add assets/reveal/   # track so the deck is offline-capable
./build.sh
open build/index.html
```

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `S` | Presenter view (current slide, next slide, speaker notes, timer) |
| `Esc` | Slide overview (bird's-eye grid) |
| `F` | Fullscreen |
| `B` | Blackout screen |
| `?` | All keyboard shortcuts |

**Speaker notes** — add a `## Notes` section to a slide's brief; it renders as `<aside class="notes">` and appears only in presenter view, never on the main slide.

**PDF export** — requires [Playwright](https://playwright.dev/) (optional):

```bash
./export.sh              # writes build/deck.pdf, one page per slide
```

---

## Design System

**`design-systems/uw-brand/DESIGN.md`** is the authoritative UW brand reference (~5,500 words) covering color tokens, typography, layout patterns, component examples, accessibility requirements, and a pre-commit checklist.

Key tokens available in all UW slides (injected via `shared/header.html`):

```css
--uw-spirit-purple: #4b2e83    /* primary brand */
--uw-spirit-gold:   #ffc700    /* accent */
--uw-husky-purple:  #32006e    /* darker variant */
--font-display:     Encode Sans
--font-body:        Open Sans
--space-4:          32px       /* 8px base scale */
--space-8:          64px
--space-16:         128px
--space-20:         160px
```

For the complete token set (semantic color aliases, weight/leading/tracking tokens, full type scale), see `design-systems/uw-brand/colors_and_type.css`.

---

## Themes

The plugin ships with two brands under `design-systems/`:

- **`uw-brand/`** — University of Washington (Husky Purple, Spirit Gold, Encode Sans)
- **`cloudbank-brand/`** — NSF CloudBank (Deep Navy, Signal Blue, Nunito + Open Sans)

Select a brand when scaffolding or reviewing:

```bash
/uw-slides:new-deck my-presentation --brand=cloudbank
/uw-slides:design-review --brand=cloudbank
/uw-slides:accessibility-check --brand=cloudbank
```

Omitting `--brand` defaults to `uw`.

### Adding a New Brand

1. Create `design-systems/<name>-brand/` with:
   - `DESIGN.md` — brand guidelines
   - `colors_and_type.css` — CSS tokens
   - `shared/header.html` — design tokens, font loading, and base styles for this brand (copy from an existing brand and modify)
2. Use `--brand=<name>` with any skill command.

---

## Skills

| Skill | Purpose |
|-------|---------|
| `new-deck` | Scaffold a new presentation directory |
| `plan-deck` | Plan a deck from a topic: objectives, layouts, slot content, `deck.yml` + briefs, approval gate before any HTML; also re-plans an existing deck |
| `generate-slides` | Generate `content/*.html` from the briefs using the layout library; skips locked slides, asks before overwriting stale ones |
| `apply-visuals` | Pass 2 — add photos, diagrams, and icons per VISUALS.md |
| `accessibility-check` | WCAG 2.1 AA validation |
| `design-review` | Brand compliance review |
| `extract-to-markdown` | Convert an existing HTML deck to `deck.yml` + `slides/*.md` briefs; `--migrate` migrates a legacy SLIDES.md deck in place |
| `update-deck` | Diff and update managed files (build scripts, shared templates, `tools/deckparse.py`) against the current plugin; never touches slides, content, or assets |

---

## Migrating from SLIDES.md

Decks built before v0.2.0 use `SLIDES.md` as the slide-ordering source. The build scripts still accept `SLIDES.md` (with a deprecation warning) but support is scheduled for removal in v0.3.0.

**One-shot migration** (from inside the deck directory):

```
/uw-slides:extract-to-markdown --migrate
```

This reads `SLIDES.md`, writes `deck.yml` + one `slides/<id>.md` brief per slide,
stamps `.uw-slides.json`, validates the output with `deckparse.py`, and removes
`SLIDES.md` (it stays in git history). Existing HTML fragments in `content/` are not
touched.

For step-by-step instructions, verification, and the manual path: see
`references/migration-guide.md` in the plugin directory.

---

## Customization

### Modifying Design Tokens

Edit `shared/header.html` in your presentation to change colors, spacing, or typography for that deck only. These changes don't affect other presentations or the plugin defaults.

### Global Defaults

To change defaults for all future presentations, edit the plugin's files. They are copied when running `/uw-slides:new-deck`:

```
design-systems/uw-brand/shared/header.html          # UW header (tokens, fonts, base styles)
design-systems/cloudbank-brand/shared/header.html   # CloudBank header
templates/shared/footer.html                        # reveal.js initialisation (shared by all brands)
templates/setup-reveal.sh                           # reveal.js asset downloader
```

Build scripts (`templates/*.sh`), `deck.yml`, `slides/`, `VISUALS.md` and `AGENTS.md` templates are copied the same way. Existing decks are not updated automatically — run `/uw-slides:update-deck` inside a deck to pull in changes from the current plugin version.

---

## Troubleshooting

**Slides don't render**
- Check that HTML files exist in `content/` with filenames matching the IDs in the `slides:` list of `deck.yml` (without `.html`); `python3 tools/deckparse.py status .` shows which slides are missing
- Each `<section>` must have `class="slide"`
- Confirm `./build.sh` ran without errors

**Wrong slide order**
- Order is determined by the `slides:` list in `deck.yml` (top to bottom), not by filename. Edit `deck.yml` to reorder.

**Images not showing**
- Image paths are relative to `build/index.html`. From there, go up one level to reach the deck root: `<img src="../assets/images/photo.jpg" alt="...">`

**Fonts not loading**
- Font paths in `shared/header.html` point to `../assets/fonts/` (relative to `build/`). For UW brand decks, Encode Sans fonts are copied to `assets/fonts/` by the `new-deck` skill. If fonts are missing, re-copy from `design-systems/uw-brand/fonts/`. CloudBank decks load fonts via Google Fonts CDN and don't require local font files.

**Build script fails**
- Confirm `shared/header.html` and `shared/footer.html` exist
- Confirm `deck.yml` has a `slides:` list (the error message gives the file and line)
- Check permissions: `chmod +x build.sh build-visuals.sh outline.sh`

**Presenter view not working (press S)**
- Run `./setup-reveal.sh` if you haven't already — it downloads `plugin/notes/notes.js` which is required for presenter view
- If the deck was scaffolded before v0.2.0, run `/uw-slides:update-deck` to pull in the updated `footer.html` that registers the notes plugin, then re-run `./setup-reveal.sh` and rebuild

**reveal.js assets not found**
- Run `./setup-reveal.sh` from inside the deck directory; it creates `assets/reveal/`
- If offline, download `reveal.min.js`, `reveal.min.css` and `plugin/notes/notes.js` manually from `https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/` and place them in `assets/reveal/`

---

## License

MIT
