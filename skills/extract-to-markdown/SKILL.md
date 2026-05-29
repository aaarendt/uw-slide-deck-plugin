---
name: extract-to-markdown
description: Convert existing monolithic HTML slide decks into markdown-per-slide format.
---

# Extract to Markdown Skill

## Purpose
Migrate existing slide decks (HTML, PowerPoint) into markdown-per-slide workflow.

## Usage
```bash
claude code /uw-slides:extract-to-markdown slides/index.html output-dir/
```

## What It Does
1. Parses input HTML or PowerPoint export
2. Extracts slides as individual markdown files
3. Generates front matter with inferred layouts
4. Creates order.txt
5. Copies images to assets/
6. Produces extraction report

## Output
```
output-dir/
├── content/*.md
├── assets/
├── order.txt
└── extraction-report.md
```

See skill documentation for supported formats.
