# Quick Start Guide

## First-Time Setup (one time only)

Create a symlink so Claude Code can find this plugin:

```bash
ln -s /home/arendta/git/aaarendt/uw-slides-plugin ~/.claude/plugins/local/uw-slides
```

This only needs to be done once. After that, the plugin is available in every Claude Code session.

## Working Inside Claude Code

All steps below are done by chatting with Claude — no terminal commands needed.

### 1. Create a New Deck

Tell Claude:
> "Create a new deck called my-talk"

Claude uses the `new-deck` skill to scaffold this structure:

```
my-talk/
├── content/
│   ├── 01-title.md
│   ├── 02-overview.md
│   └── 03-conclusion.md
├── assets/
├── order.txt
└── README.md
```

### 2. Edit Your Slides

Each slide is a markdown file in `content/`. Edit them directly in VS Code:

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

Reorder slides by editing `order.txt`.

### 3. Render

Tell Claude:
> "Render my deck"

Claude generates `build/index.html`. Open it in a browser to preview.

### 4. Validate

Tell Claude:
> "Check accessibility" or "Review the design"

Claude runs WCAG 2.1 AA checks and UW brand compliance review, reporting any issues.

---

See `README.md` for the full reference guide.
