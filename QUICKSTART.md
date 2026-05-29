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
