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
```

## Architecture Overview

This skill creates a **fragment-based** presentation:
- Each slide is a complete HTML `<section>` with inline scoped styles
- Build process is simple concatenation (no templating, no parsing)
- Easy reordering via `SLIDES.md` (master planning document)
- Full LLM creative freedom within UW brand guidelines

## Generated Directory Structure

```
<presentation-name>/
├── shared/
│   ├── header.html              # Design tokens, base styles
│   └── footer.html              # Navigation, closing tags
├── content/                     # Pass-1 slide fragments (LLM writes here)
├── content-with-visuals/        # Pass-2 slide fragments (apply-visuals writes here)
├── assets/
│   ├── images/
│   └── diagrams/
├── SLIDES.md                    # Pass 1: slide order, content briefs, render instructions
├── VISUALS.md                   # Pass 2: per-slide visual additions
├── build.sh                     # Pass 1: concatenate content/ → build/index.html
├── build-visuals.sh             # Pass 2: concatenate content-with-visuals/ → build/index-with-visuals.html
└── README.md                    # User instructions
```

## Workflow

1. **Scaffold:** Run this skill to create directory structure
2. **Plan:** Edit `SLIDES.md` to outline your presentation
3. **Create slides:** Request slides via conversation (LLM reads SLIDES.md, writes to `content/`)
4. **Build pass 1:** Run `./build.sh` → `build/index.html`
5. **Rehearse:** Present from `build/index.html`; revise `SLIDES.md` and rebuild as needed
6. **Plan visuals:** Edit `VISUALS.md` once content is settled
7. **Apply visuals:** Run `/uw-slides:apply-visuals` (LLM reads VISUALS.md, writes to `content-with-visuals/`)
8. **Build pass 2:** Run `./build-visuals.sh` → `build/index-with-visuals.html`

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
- Colors: `--uw-spirit-purple`, `--uw-husky-purple`, `--uw-spirit-gold`, `--uw-husky-gold-web`, `--uw-heritage-gold`, `--uw-white`, `--uw-black`, `--uw-gray-90`, etc.
- Fonts: `--font-display`, `--font-display-wide`, `--font-display-compressed`, `--font-body`
- Spacing: `--space-1` (8px) through `--space-12` (96px)

**Design Freedom:**
- Any HTML structure
- Any CSS layout (grid, flexbox, absolute positioning, etc.)
- Custom typography hierarchy
- Unique layouts per slide type
- Creative use of space and composition

## When User Requests a Slide

1. **Read SLIDES.md** to understand the overall presentation plan
2. **Ask clarifying questions** about content and purpose
3. **Design the structure** based on content needs (not templates)
4. **Generate complete HTML fragment** following the pattern above
5. **Save to** `content/NN-description.html`
6. **Add slide heading** `## NN-description` to `SLIDES.md` (if not already there)
7. **Instruct user** to run `./build.sh` to rebuild

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
Copy from plugin templates directory:
- `shared/header.html` from `~/.claude/plugins/local/uw-slides/templates/shared/header.html`
- `shared/footer.html` from `~/.claude/plugins/local/uw-slides/templates/shared/footer.html`
- `build.sh` from `~/.claude/plugins/local/uw-slides/templates/build.sh`
- `build-visuals.sh` from `~/.claude/plugins/local/uw-slides/templates/build-visuals.sh`
- `SLIDES.md` from `~/.claude/plugins/local/uw-slides/templates/SLIDES.md`
- `VISUALS.md` from `~/.claude/plugins/local/uw-slides/templates/VISUALS.md`

### 2. Copy UW brand fonts
Copy all Encode Sans fonts from plugin to presentation:
- Copy `~/.claude/plugins/local/uw-slides/design-system/fonts/*` to `assets/fonts/`
- This includes 45 .ttf files (~9MB total) for all Encode Sans variants
- Ensures presentations are self-contained and portable

### 3. Create empty directories
- `content/` (empty — pass-1 slides added here via conversation)
- `content-with-visuals/` (empty — pass-2 output written here by apply-visuals)
- `assets/images/`
- `assets/diagrams/`

### 3. Customize SLIDES.md
```markdown
# [Presentation Name]

Brief description of the presentation.

## 01-title

Title slide notes and planning...

## 02-overview

Overview slide content ideas...
```

### 4. Create README.md
```markdown
# [Presentation Name]

UW-branded presentation using a two-pass, fragment-based architecture.

## Pass 1 — Content and structure

1. Edit `SLIDES.md` to plan your presentation
2. Request slides through conversation (LLM reads SLIDES.md, writes to `content/`)
3. Build: `./build.sh`
4. Preview: `open build/index.html`
5. Rehearse and revise — repeat until content is settled

## Pass 2 — Visual additions

1. Edit `VISUALS.md` to specify photographs, diagrammatic accents, and icons
2. Run `/uw-slides:apply-visuals` (LLM reads VISUALS.md, writes to `content-with-visuals/`)
3. Build: `./build-visuals.sh`
4. Preview: `open build/index-with-visuals.html`

## Reordering Slides

Edit the `## slide-id` order in `SLIDES.md`, then rebuild with `./build.sh`.

## Structure

- `SLIDES.md` — Pass-1 planning document (slide order + content briefs)
- `VISUALS.md` — Pass-2 visual additions specification
- `content/` — Pass-1 HTML fragments (source of truth; never modified by pass 2)
- `content-with-visuals/` — Pass-2 HTML fragments (only slides that received additions)
- `shared/` — Header and footer templates
- `build/` — Generated presentations (git-ignored)
- `assets/` — Images and diagrams
```

### 5. Create .gitignore
```
build/
.DS_Store
*.swp
*~
```

## Success Message

After scaffolding, tell the user:

```
✓ Created UW presentation: <presentation-name>/

Pass 1 — content and structure:
1. cd <presentation-name>
2. Edit SLIDES.md to outline your presentation
3. Request slides (e.g., "Create slide 01-title for my talk on...")
4. Build: ./build.sh
5. Preview: open build/index.html
6. Rehearse and revise until content is settled

Pass 2 — visual additions (after content is settled):
1. Edit VISUALS.md to specify photos, icons, and diagrammatic accents
2. Run /uw-slides:apply-visuals
3. Build: ./build-visuals.sh
4. Preview: open build/index-with-visuals.html

Each slide is a self-contained HTML fragment with inline scoped styles.
Full creative freedom within UW brand guidelines.
```
