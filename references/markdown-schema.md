# Markdown Front Matter Schema (legacy)

> **Superseded by [slide-schema.md](slide-schema.md)**, which defines `deck.yml`
> and `slides/<id>.md` briefs (`id` replaces `slide_id`, and so on). The field
> mapping is in its "Mapping from older formats" section. This file remains only
> as a reference for decks that still use it.

## Required Fields

```yaml
---
slide_id: unique-identifier    # kebab-case (01-title, 02-overview)
title: "Slide Title"           # Main heading
layout: template-name          # title, two-column, image-bottom, etc.
background: color-name         # spirit-purple, husky-purple, or white
---
```

## Optional Fields

```yaml
section: "Deck Section"        # Logical grouping
duration_min: 2                # Estimated speaking time
presenter: "Name"              # Who presents
accent_bar: top                # 'top' or 'left' (default: top)
eyebrow: "LABEL"               # Uppercase label above title
alt_texts:                     # Image descriptions
  image.png: "Description"
```

## Content Sections

```markdown
## Key message
One-sentence takeaway

## Talking points
- First point
- Second point

## Visual notes
- Layout guidance
- Image placement

## Speaker notes
Full narration script
```

## Available Layouts
- `title` — Title slide with logos
- `two-column` — Side-by-side content  
- `image-bottom` — Content + large image
- `comparison` — Before/after
- `code` — Code snippets
- `transition` — Section breaks
- `architecture` — Diagrams

See plugin templates for implementation. The current layout set and the mapping from these names is in [layouts.md](layouts.md).
