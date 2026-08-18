# UW Slides Plugin

Create branded presentations with any LLM using a fragment-based architecture. Ships with University of Washington and CloudBank themes; extensible to additional brands.

## Features

- **LLM-agnostic:** Works with Claude, GPT, Gemini, Llama, etc.
- **Fragment-based:** Each slide is self-contained HTML with inline scoped styles
- **Two-pass workflow:** Pass 1 builds content and layout; pass 2 adds visuals
- **SLIDES.md-driven:** Slide order and content intent live in one planning document
- **UW brand compliant:** Design system documented in `design-systems/uw-brand/DESIGN.md`
- **WCAG 2.1 AA accessible:** Built-in accessibility requirements
- **Simple build:** Bash scripts, no Python/Node/parsing

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

# Plan your deck — edit SLIDES.md, then generate slides via conversation:
"Create slide 1 based on SLIDES.md"

# Build and preview
cd my-presentation
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
│   └── footer.html            # Navigation JS, closing tags
├── content/                   # Pass-1 slide fragments (text, layout, color)
├── content-with-visuals/      # Pass-2 slide fragments (adds photos, diagrams)
├── assets/
│   ├── images/
│   └── diagrams/
├── SLIDES.md                  # Planning document — defines order and content intent
├── VISUALS.md                 # Pass-2 additions spec — photos, diagrams, icons
├── build.sh                   # Pass-1 build: content/ → build/index.html
└── build-visuals.sh           # Pass-2 build: content-with-visuals/ → build/index-with-visuals.html
```

### SLIDES.md Is the Source of Truth

`SLIDES.md` controls both slide content intent and build order. The build script reads `## slide-id` headings (top to bottom) to determine which fragments to concatenate and in what sequence. Moving a heading in SLIDES.md reorders the built presentation.

Write SLIDES.md in plain prose — bullet points, speaker notes, key messages, whatever helps. The LLM reads it to generate slides; there's no required format beyond the `## slide-id` headings.

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

### Two-Pass Workflow

**Pass 1 — content and structure:**
1. Edit `SLIDES.md` with your slide content and intent
2. Generate `content/*.html` fragments via conversation with your LLM
3. Run `./build.sh` → `build/index.html`
4. The deck should look complete at this stage — no image placeholders

**Pass 2 — visual additions:**
1. Specify photographs, diagrams, and icons in `VISUALS.md`
2. Run `/uw-slides:apply-visuals` → writes to `content-with-visuals/`
3. Run `./build-visuals.sh` → `build/index-with-visuals.html`

Pass 2 is additive. Slides not listed in VISUALS.md are served unchanged from `content/`. Pass 2 never modifies pass-1 files.

### Navigation

- Arrow keys, Space, PageUp/PageDown: advance/retreat
- Home/End: jump to first/last slide
- Click anywhere: advance to next slide
- Slide counter: bottom right

---

## Design System

Read **`design-systems/uw-brand/DESIGN.md`** before generating any slide HTML. It is the authoritative UW brand reference (~5,500 words) covering color tokens, typography, layout patterns, component examples, accessibility requirements, and a pre-commit checklist.

Key tokens available in all UW slides (injected via `shared/header.html`):

```css
--uw-spirit-purple: #4b2e83    /* primary brand */
--uw-spirit-gold:   #ffc700    /* accent */
--uw-husky-purple:  #32006e    /* darker variant */
--font-display:     Encode Sans
--font-body:        Open Sans
--space-4:          16px       /* 4px base scale */
--space-8:          32px
--space-16:         64px
--space-20:         80px
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
| `apply-visuals` | Pass 2 — add photos, diagrams, and icons per VISUALS.md |
| `accessibility-check` | WCAG 2.1 AA validation |
| `design-review` | Brand compliance review |
| `extract-to-markdown` | Convert an existing HTML deck to a SLIDES.md outline |

---

## Customization

### Modifying Design Tokens

Edit `shared/header.html` in your presentation to change colors, spacing, or typography for that deck only. These changes don't affect other presentations or the plugin defaults.

### Global Defaults

To change defaults for all future presentations, edit the plugin's template files:

```
design-systems/uw-brand/templates/shared/header.html
design-systems/uw-brand/templates/shared/footer.html
```

These are copied when running `/uw-slides:new-deck`.

---

## Tips

- Write SLIDES.md before asking your LLM to generate HTML. A clear content brief produces better slides than generating ad hoc.
- Be specific: "Create a two-column comparison slide with purple background and gold accent on the left column."
- If a slide feels visually sparse, the right response is stronger typography or layout — not adding a placeholder image.
- Text must fit the slide. If content overflows, reduce the amount of text, not the font size. All visible text must be at least `1.5rem` (24pt) — anything smaller is invisible past the third row.
- Always include `alt` text on images and use semantic HTML (`<h1>`, `<ul>`, etc.).

---

## Troubleshooting

**Slides don't render**
- Check that HTML files exist in `content/` with filenames matching the `## slide-id` headings in SLIDES.md (without `.html`)
- Each `<section>` must have `class="slide"`
- Confirm `./build.sh` ran without errors

**Wrong slide order**
- Order is determined by `## slide-id` sequence in SLIDES.md (top to bottom), not by filename. Edit SLIDES.md to reorder.

**Images not showing**
- Image paths are relative to `build/index.html`. From there, go up one level to reach the deck root: `<img src="../assets/images/photo.jpg" alt="...">`

**Fonts not loading**
- Font paths in `shared/header.html` point to `../assets/fonts/` (relative to `build/`). For UW brand decks, Encode Sans fonts are copied to `assets/fonts/` by the `new-deck` skill. If fonts are missing, re-copy from `design-systems/uw-brand/fonts/`. CloudBank decks load fonts via Google Fonts CDN and don't require local font files.

**Build script fails**
- Confirm `shared/header.html` and `shared/footer.html` exist
- Confirm SLIDES.md contains `## slide-id` headings
- Check permissions: `chmod +x build.sh build-visuals.sh`

---

## License

MIT
