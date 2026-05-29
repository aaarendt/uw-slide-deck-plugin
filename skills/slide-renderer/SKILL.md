---
name: slide-renderer
description: Render UW-branded HTML slide deck from markdown source files. Reads order.txt manifest and content/*.md files, applies UW design system, validates accessibility, and generates build/index.html.
---

# Slide Renderer Skill

## Purpose
Generate complete UW-branded HTML slide deck from markdown source files.

## Input Requirements

### Directory Structure
```
./
├── content/              # Markdown files (one per slide)
├── order.txt             # Slide sequence
├── assets/               # Images
└── build/                # Output (created)
```

### order.txt Format
```
# Comments start with #
01-title.md
02-overview.md
03-content.md
```

### Markdown Front Matter
```yaml
---
slide_id: unique-id
title: "Slide Title"
layout: template-name
background: spirit-purple | white
---
```

## Available Layouts
- `title` — Title slide with logos
- `two-column` — Side-by-side content
- `image-bottom` — Content above, image below
- `comparison` — Before/after comparison
- `code` — Code snippets
- `transition` — Section breaks
- `architecture` — Diagram-focused

## Usage
```bash
claude code /uw-slides:render
```

See `references/markdown-schema.md` for complete specification.
