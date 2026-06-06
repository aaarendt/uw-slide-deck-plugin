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
│   ├── header.html          # Design tokens, base styles
│   └── footer.html          # Navigation, closing tags
├── content/                 # (empty - user adds slides)
├── assets/
│   ├── images/
│   └── diagrams/
├── SLIDES.md                # Master document: slide order + planning notes
├── build.sh                 # Concatenation script
└── README.md               # User instructions
```

## Workflow

1. **Scaffold:** Run this skill to create directory structure
2. **Plan:** Edit `SLIDES.md` to outline your presentation
3. **Create slides:** Request slides via conversation (LLM reads SLIDES.md)
4. **Generate fragments:** LLM creates self-contained HTML sections
5. **Build:** Run `./build.sh` to concatenate into single HTML file
6. **Reorder:** Edit slide order in `SLIDES.md` and rebuild

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
- `SLIDES.md` from `~/.claude/plugins/local/uw-slides/templates/SLIDES.md`

### 2. Copy UW brand fonts
Copy all Encode Sans fonts from plugin to presentation:
- Copy `~/.claude/plugins/local/uw-slides/design-system/fonts/*` to `assets/fonts/`
- This includes 45 .ttf files (~9MB total) for all Encode Sans variants
- Ensures presentations are self-contained and portable

### 3. Create empty directories
- `content/` (empty - slides added later)
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

UW-branded presentation using fragment-based architecture.

## Quick Start

1. Edit `SLIDES.md` to plan your presentation
2. Request slides through conversation with your LLM
3. Build: `./build.sh`
4. Preview: `open build/index.html`

## Reordering Slides

Edit the `## slide-id` order in `SLIDES.md`, then rebuild.

## Structure

- `SLIDES.md` - Master planning document (defines slide order)
- `content/` - Individual slide HTML fragments
- `shared/` - Header and footer templates
- `build/` - Generated presentation (git-ignored)
- `assets/` - Images and diagrams

## Creating Slides

Each slide is a self-contained HTML fragment with:
- Unique `data-slide` attribute
- Inline scoped styles
- UW brand compliance

See plugin documentation for complete guidelines.
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

Next steps:
1. cd <presentation-name>
2. Request your first slide (e.g., "Create a title slide for my talk on...")
3. Build with: ./build.sh
4. Preview with: open build/index.html

The presentation uses a fragment-based architecture where each slide is a 
self-contained HTML file with inline styles. You have full creative freedom 
within UW brand guidelines.
```
