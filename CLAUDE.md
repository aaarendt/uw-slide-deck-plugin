# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Plugin Does

This is a Claude Code plugin (`uw-slides`) for creating University of Washington branded HTML presentations. The plugin lives in `~/.claude/plugins/local/uw-slides/` (symlinked) and exposes skills to Claude Code sessions in any project directory.

No build system, no dependencies — just bash scripts and HTML fragments.

## Plugin Structure

```
uw-slides-plugin/
├── .claude-plugin/          # Plugin metadata (plugin.json, marketplace.json)
├── skills/                  # Claude Code skill definitions
│   ├── new-deck/SKILL.md
│   ├── accessibility-check/SKILL.md
│   ├── apply-visuals/SKILL.md
│   ├── design-review/SKILL.md
│   └── extract-to-markdown/SKILL.md
├── templates/               # Scaffolding source copied to new presentations
│   ├── shared/              # header.html and footer.html
│   ├── examples/            # Reference HTML fragments
│   ├── build.sh             # Pass-1 build script template
│   ├── build-visuals.sh     # Pass-2 build script template
│   ├── SLIDES.md            # Planning document template
│   └── VISUALS.md           # Visual additions template
├── design-system/
│   ├── DESIGN.md            # Authoritative UW brand guidelines (~5500 words)
│   ├── colors_and_type.css  # Design tokens and @font-face declarations
│   └── fonts/               # Encode Sans (45 variants: 5 widths × 9 weights)
└── references/
    ├── accessibility-requirements.md
    └── markdown-schema.md
```

## Slide Fragment Architecture

Each slide is a self-contained `<section>` saved as `content/<slide-id>.html`. Styles are **inline and scoped** using the attribute selector pattern:

```html
<section data-slide="03-approach" aria-label="Slide 3: Our Approach" class="slide">
  <div class="content">...</div>
  <style>
    section[data-slide="03-approach"] { background: var(--uw-spirit-purple); }
    section[data-slide="03-approach"] h1 { font-family: var(--font-display); }
  </style>
</section>
```

The `section[data-slide="..."]` scoping is critical — it prevents cascade conflicts between slides with no class name collisions.

## Two-Pass Workflow

**Pass 1 (content):** SLIDES.md → `content/*.html` fragments → `build.sh` → `build/index.html`

**Pass 2 (visuals):** VISUALS.md → `/uw-slides:apply-visuals` → `content-with-visuals/*.html` → `build-visuals.sh` → `build/index-with-visuals.html`

Pass 2 only modifies slides listed in VISUALS.md under `## Per-slide additions`. Unmodified slides are served from `content/` as fallback. Pass 2 never rebuilds from scratch.

## SLIDES.md Is the Source of Truth

`SLIDES.md` controls slide ordering and content intent. The build script reads `## slide-id` headings to determine both the slide list and concatenation order. Moving a heading in SLIDES.md reorders the built presentation.

Key authoring rules for SLIDES.md (enforced by skill behavior, not code):
- **Key message** = the one thing shown large on the slide
- **Bullets** = talking points spoken aloud, not rendered verbatim
- **Note to self** = speaker-only, never rendered
- Pass 1 uses no photographs or decorative icons — layout/typography/color only

## Build Commands

From inside a generated presentation directory:

```bash
./build.sh                  # Pass 1 → build/index.html
./build-visuals.sh          # Pass 2 → build/index-with-visuals.html
```

The build scripts accept an optional directory argument: `./build.sh /path/to/deck`

## Available Skills

| Skill | Purpose |
|-------|---------|
| `/uw-slides:new-deck <name>` | Scaffold a new presentation directory |
| `/uw-slides:apply-visuals` | Run pass 2 — add visuals per VISUALS.md |
| `/uw-slides:accessibility-check` | WCAG 2.1 AA validation |
| `/uw-slides:design-review` | UW brand compliance check |
| `/uw-slides:extract-to-markdown` | Convert existing HTML deck → SLIDES.md outline |

## Design System

Read `design-system/DESIGN.md` before generating any slide HTML. Key tokens available in all slides (injected via `shared/header.html`):

```css
--uw-spirit-purple: #4b2e83
--uw-spirit-gold:   #ffc700
--uw-husky-purple:  #32006e
--font-display:     Encode Sans
--font-body:        Open Sans
--space-1 … --space-12  /* 8px grid: 8px–96px */
```

Every slide should have an 8px gold accent bar (`--uw-spirit-gold`), typically `::before` on the `<section>`.

## Font Size Rules (Enforced at Generation Time)

Slides are projected to a live audience. Small text is invisible past the third row. **Apply these rules when writing every slide, not after the fact:**

- **All visible text:** minimum `1.5rem` (24pt) — use `clamp(1.5rem, <vw>, <max>)`
- **Source/citation lines only:** `clamp(1rem, 1.1vw, 1.25rem)` — the one exception
- **Never use fixed values below 1.5rem** for any text element
- **The vw midpoint must scale above the minimum** — use at least `2vw` for body text
- **Body/description text:** `clamp(1.5rem, 1.6–2.2vw, 1.625–2rem)`
- **Key message / headline:** `clamp(1.5rem, 2.5–2.8vw, 2.25–2.5rem)` or larger
- **Labels / uppercase tags:** `clamp(1rem, 1.2vw, 1.25rem)` — decorative, not primary content
- **Text must fit on the slide** — if content overflows, reduce the amount of text, not the font size

These rules are also checked by `/uw-slides:design-review`.

## Generated Presentation Layout

When `/uw-slides:new-deck` runs, the presentation gets:

```
<name>/
├── shared/header.html       # CSS variables, font-face, base styles
├── shared/footer.html       # Keyboard navigation JS, closing tags
├── content/                 # Slide HTML fragments (empty initially)
├── content-with-visuals/    # Created by apply-visuals (pass 2)
├── assets/images/
├── SLIDES.md                # Planning document (governs build order)
├── VISUALS.md               # Pass-2 visual additions spec
├── build.sh
└── build-visuals.sh
```

Font paths in `shared/header.html` are relative to the plugin install path (`../../design-system/fonts/`). If the plugin is not at `~/.claude/plugins/local/uw-slides/`, update those paths.

## Skill Development Notes

Each skill is defined by a `SKILL.md` in `skills/<skill-name>/`. To add or modify a skill:
1. Edit or create `skills/<skill-name>/SKILL.md`
2. Update `.claude-plugin/plugin.json` if adding a new skill entry
3. Test by running the skill from a presentation directory

Skills run in the context of the **presentation directory** (wherever the user is), not the plugin directory.
