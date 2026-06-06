---
name: extract-to-markdown
description: Extract slide content from HTML presentations to create a SLIDES.md planning document
---

# Extract to Markdown Skill

## Purpose
Create a SLIDES.md outline from existing HTML slide decks to help plan new fragment-based presentations.

## Usage
```bash
/uw-slides:extract-to-markdown slides/index.html
```

## What It Does
1. Parses HTML slide deck
2. Extracts slide content (headings, text, structure)
3. Generates SLIDES.md with slide outlines
4. Notes image references
5. Produces extraction report

## Output
Creates `SLIDES.md` in the current directory:

```markdown
# Extracted Presentation

## 01-title
Title: Original Title
Content: Extracted text...

## 02-content
Main points:
- Point 1
- Point 2

Images: diagram.png
```

This serves as a starting point for planning your fragment-based presentation.

## Note
This skill extracts content outline only - you'll still need to ask your LLM to generate the actual HTML slide fragments based on the SLIDES.md plan.
