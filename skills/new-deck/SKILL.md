---
name: new-deck
description: Scaffold new UW presentation with fragment-based architecture
---

# New UW Presentation Deck (Fragment-Based)

## Purpose
Create a UW-branded presentation using a modular, LLM-first architecture where each slide is a self-contained HTML fragment.

## Usage
```bash
/uw-slides:new-deck <presentation-name>
/uw-slides:new-deck <presentation-name> --brand=cloudbank
```

The optional `--brand=<uw|cloudbank>` parameter selects the design system. Defaults to `uw`.

## Architecture Overview

This skill creates a **fragment-based** presentation:
- Each slide is a complete HTML `<section>` with inline scoped styles
- Build process is simple concatenation in the order listed in `deck.yml`
- Each slide has a brief in `slides/<id>.md` (message, layout, notes, owner, status); the HTML is generated from it
- Layouts come from the layout library (`references/layouts.md`), with `layout: custom` as the escape hatch
- Easy reordering: move a line in `deck.yml`

## Generated Directory Structure

```
<presentation-name>/
├── shared/
│   ├── header.html              # Design tokens, base styles
│   └── footer.html              # Navigation, closing tags
├── deck.yml                     # Deck metadata, objectives and slide order (source of truth for order)
├── slides/                      # One brief per slide: slides/<id>.md (source of truth for content)
├── content/                     # Pass-1 slide fragments (generate-slides writes here)
├── content-with-visuals/        # Pass-2 slide fragments (apply-visuals writes here)
├── assets/
│   ├── images/
│   └── diagrams/
├── OUTLINE.md                   # Generated read-only overview (created by ./outline.sh)
├── VISUALS.md                   # Pass 2: per-slide visual additions
├── build.sh                     # Pass 1: concatenate content/ → build/index.html
├── outline.sh                   # Regenerate OUTLINE.md from deck.yml + slides/
├── build-visuals.sh             # Pass 2: concatenate content-with-visuals/ → build/index-with-visuals.html
├── publish.sh                   # Pass 3: inline images as base64 → build/index-published.html
└── README.md                    # User instructions
```

## Workflow

1. **Scaffold:** Run this skill to create directory structure
2. **Plan:** Edit `deck.yml` (order) and `slides/<id>.md` (one brief per slide)
3. **Create slides:** Run `/uw-slides:generate-slides` (reads the briefs, writes `content/`)
4. **Build pass 1:** Run `./build.sh` → `build/index.html`
5. **Rehearse:** Present from `build/index.html`; revise the briefs, regenerate and rebuild as needed
6. **Plan visuals:** Edit `VISUALS.md` once content is settled
7. **Apply visuals:** Run `/uw-slides:apply-visuals` (LLM reads VISUALS.md, writes to `content-with-visuals/`)
8. **Build pass 2:** Run `./build-visuals.sh` → `build/index-with-visuals.html`
9. **Publish:** Run `./publish.sh` → `build/index-published.html` (all images inlined as base64 for a fully self-contained portable file)

## Slide Fragment Pattern

Each slide must follow this pattern:

```html
<section data-slide="NN-descriptive-name" 
         aria-label="Slide N: Title Here"
         class="slide">
  
  <!-- Content structure (any HTML the LLM designs) -->
  <div class="container">
    <h1>Title</h1>
    <p>Content...</p>
  </div>

  <!-- Scoped styles using attribute selector -->
  <style>
    section[data-slide="NN-descriptive-name"] {
      /* All styles scoped to this section only */
      background: var(--uw-spirit-purple);
      display: grid;
      grid-template-columns: 1fr 1fr;
      /* ... custom layout ... */
    }
    
    section[data-slide="NN-descriptive-name"] h1 {
      font-family: var(--font-display);
      /* ... custom typography ... */
    }
  </style>
</section>
```

## Key Constraints

**Required:**
- `data-slide` attribute with unique ID
- `aria-label` for accessibility
- `class="slide"` for navigation system
- All styles scoped with `section[data-slide="..."]` selector
- Follow UW brand colors (use CSS variables from header)
- Minimum 24px font size (WCAG 2.1 AA)
- 4.5:1 contrast ratio minimum

**Available CSS Variables (from header.html):**

For `--brand=uw`:
- Colors: `--uw-spirit-purple`, `--uw-husky-purple`, `--uw-spirit-gold`, `--uw-husky-gold-web`, `--uw-heritage-gold`, `--uw-white`, `--uw-black`, `--uw-gray-90`, etc.
- Fonts: `--font-display` (Encode Sans), `--font-display-wide`, `--font-display-compressed`, `--font-display-narrow`, `--font-display-condensed`, `--font-body` (Open Sans), `--font-mono`
- Spacing: `--space-1` (8px) through `--space-20` (160px); common: `--space-8` 64px, `--space-16` 128px, `--space-20` 160px

For `--brand=cloudbank`:
- Colors: `--cb-deep-navy`, `--cb-signal-blue`, `--cb-ink`, `--cb-mist`, `--cb-fog`, `--cb-white`, `--cb-black`, etc.
- Semantic aliases: `--bg-primary`, `--bg-surface`, `--text-body`, `--text-on-dark`, `--border-accent`, etc.
- Fonts: `--font-display` (Nunito), `--font-body` (Open Sans)
- Spacing: `--space-1` (8px) through `--space-20` (160px); common: `--space-8` 64px, `--space-16` 128px, `--space-20` 160px

**Design Freedom:**
- Layouts come from the library (`references/layouts.md`); `layout: custom` allows any HTML structure and CSS layout within the brand rules
- Within a slide, keep to the brand tokens and the type scale

## When User Requests a Slide

Slides are generated from briefs by `/uw-slides:generate-slides`. If the user asks for a new slide by conversation:

1. **Read `deck.yml` and the existing briefs** to understand the plan
2. **Ask clarifying questions** about the message and purpose
3. **Write `slides/<id>.md`** (front matter and `# Key message`; see `references/slide-schema.md`) and **add the ID to `deck.yml`** at the right position
4. **Run `/uw-slides:generate-slides <id>`** to create `content/<id>.html`
5. **Instruct user** to run `./build.sh` to rebuild

## Build and Preview

```bash
# Build presentation
./build.sh

# Preview in browser
open build/index.html
```

## Accessibility Checklist

Every slide must meet WCAG 2.1 Level AA:
- All images have `alt` text
- Text size ≥ 24px
- Contrast ratio ≥ 4.5:1
- Semantic HTML (`<h1>`, `<p>`, `<ul>`, etc.)
- Keyboard navigation supported (automatic via footer.html)
- `aria-label` on section

## Implementation

When this skill is invoked, create the following files:

### 1. Copy shared templates
Brand-agnostic files come from the root templates directory; only `header.html` is brand-specific.

Brand-agnostic (same for all brands):
- `shared/footer.html` from `~/.claude/plugins/local/uw-slides/templates/shared/footer.html`
- `build.sh` from `~/.claude/plugins/local/uw-slides/templates/build.sh`
- `build-visuals.sh` from `~/.claude/plugins/local/uw-slides/templates/build-visuals.sh`
- `outline.sh` from `~/.claude/plugins/local/uw-slides/templates/outline.sh`
- `publish.sh` from `~/.claude/plugins/local/uw-slides/templates/publish.sh`
- `VISUALS.md` from `~/.claude/plugins/local/uw-slides/templates/VISUALS.md`

Do **not** create a `SLIDES.md`: `deck.yml` and `slides/` replace it. Keep the scripts executable.

Brand-specific (use the `--brand` value, default: `uw`):
- `shared/header.html` from `~/.claude/plugins/local/uw-slides/design-systems/${brand}-brand/shared/header.html`

Write a `.brand` file to the presentation root containing just the brand name and a trailing newline (e.g. `uw\n` or `cloudbank\n`). This file is read by all other skills to auto-detect the brand without requiring a `--brand=` flag on every invocation. It should be git-tracked.

### 2. Copy brand fonts (UW only)
For `--brand=uw`: copy all Encode Sans fonts from plugin to presentation:
- Copy `~/.claude/plugins/local/uw-slides/design-systems/uw-brand/fonts/*` to `assets/fonts/`
- This includes 45 .ttf files (~9MB total) for all Encode Sans variants
- Ensures presentations are self-contained and portable

For `--brand=cloudbank`: **skip font copy.** CloudBank uses Nunito and Open Sans loaded via Google Fonts CDN — no local font files needed.

### 3. Create empty directories
- `content/` (empty — pass-1 slides are written here by generate-slides)
- `content-with-visuals/` (empty — pass-2 output written here by apply-visuals)
- `assets/images/`
- `assets/diagrams/`

### 4. Create deck.yml and the starter briefs
Copy `~/.claude/plugins/local/uw-slides/templates/deck.yml` to `deck.yml` and set `title:` to the presentation name. Keep its `slides:` list as `title` then `example-slide`, and create the matching briefs in `slides/`:

- `slides/example-slide.md`: copy `~/.claude/plugins/local/uw-slides/templates/slides/_example.md` (its `id` is already `example-slide`).
- `slides/title.md`:

```markdown
---
id: title
layout: title
status: draft
---

# Key message
[Presentation Name]

## Slot: subtitle
Subtitle
```

Validate: `python3 ~/.claude/plugins/local/uw-slides/tools/deckparse.py deck deck.yml` must succeed. Do not create `content/` fragments here: `/uw-slides:generate-slides` writes them.

### 5. Create README.md
Copy `~/.claude/plugins/local/uw-slides/templates/README.md`, then replace:
- `[Presentation Name]` with the actual presentation name
- `[BRAND_NAME]` with the brand's display name (`UW-branded` or `CloudBank-branded`)

### 6. Create .gitignore
```
build/
.DS_Store
*.swp
*~
```

### 7. Create AGENTS.md
Copy `~/.claude/plugins/local/uw-slides/templates/AGENTS.md`, then replace:
- `[Presentation Name]` with the actual presentation name
- `[BRAND]` with the brand value (`uw` or `cloudbank`)

### 8. Create CLAUDE.md
Copy `~/.claude/plugins/local/uw-slides/templates/CLAUDE.md` verbatim (no substitutions needed).

## Success Message

After scaffolding, tell the user:

```
✓ Created UW presentation: <presentation-name>/

Pass 1 — content and structure:
1. cd <presentation-name>
2. Edit deck.yml (title, audience, objectives, slide order) and the briefs in slides/
3. Run /uw-slides:generate-slides to create the slide HTML in content/
4. Build: ./build.sh
5. Preview: open build/index.html
6. Rehearse; revise the briefs, regenerate and rebuild until content is settled
7. Optional: ./outline.sh writes OUTLINE.md, a read-only overview

Pass 2 — visual additions (after content is settled):
1. Edit VISUALS.md to specify photos, icons, and diagrammatic accents
2. Run /uw-slides:apply-visuals
3. Build: ./build-visuals.sh
4. Preview: open build/index-with-visuals.html

Pass 3 — publish (portable, self-contained file):
1. Run: ./publish.sh
2. Share: build/index-published.html (all images inlined as base64)

Each slide is a self-contained HTML fragment with inline scoped styles,
generated from its brief using the layout library.
```
