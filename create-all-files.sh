#!/bin/bash

# This script recreates all plugin files

echo "Creating README.md..."
cat > README.md << 'EOF'
# UW Slides Plugin

A Claude Code plugin for creating University of Washington branded slide decks with built-in accessibility compliance (WCAG 2.1 AA) and a markdown-per-slide workflow.

## Quick Start

```bash
# Install plugin
ln -s /path/to/uw-slides-plugin ~/.claude/plugins/local/uw-slides

# Create new presentation
claude code /uw-slides:new-deck my-talk

# Render slides
cd my-talk
claude code /uw-slides:render

# View
open build/index.html
```

## Features

- ✅ Markdown-per-slide workflow (clean diffs, easy reordering)
- ✅ UW brand compliance built-in
- ✅ WCAG 2.1 AA accessibility validation
- ✅ Reusable across all presentations
- ✅ order.txt for easy slide reordering

## Skills

- `/uw-slides:render` — Generate HTML deck
- `/uw-slides:accessibility-check` — WCAG validation
- `/uw-slides:design-review` — Brand compliance
- `/uw-slides:new-deck` — Scaffold new presentation
- `/uw-slides:extract-to-markdown` — Convert HTML → markdown

## Documentation

- `QUICKSTART.md` — 5-minute tutorial
- `HOW-TO-CREATE-TEMPLATES.md` — Extract layout templates
- `CONTRIBUTING.md` — Developer guide
- `TODO.md` — What's next

## License

MIT License - see LICENSE file
EOF

echo "Creating QUICKSTART.md (abbreviated)..."
cat > QUICKSTART.md << 'EOF'
# Quick Start Guide

## Installation

```bash
ln -s /path/to/uw-slides-plugin ~/.claude/plugins/local/uw-slides
```

## Create First Deck

```bash
claude code /uw-slides:new-deck my-talk
cd my-talk
```

## Edit Slides

Edit `content/*.md` files:

```yaml
---
slide_id: 01-title
title: "My Research"
layout: title
background: spirit-purple
---

## Key message
Main takeaway

## Speaker notes
What I'll say...
```

## Render

```bash
claude code /uw-slides:render
open build/index.html
```

## Validation

```bash
claude code /uw-slides:accessibility-check
claude code /uw-slides:design-review
```

See full guide in main README.md
EOF

echo "All documentation files created!"
