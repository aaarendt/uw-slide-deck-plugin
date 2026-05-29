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
