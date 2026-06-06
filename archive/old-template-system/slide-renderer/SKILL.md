# Slide Renderer Skill

## Purpose
Generate complete UW-branded HTML slide deck from markdown source files using Jinja2 templates.

## What This Does
1. Reads your markdown slides from `content/` directory
2. Parses YAML frontmatter and markdown content
3. Applies professional UW-branded HTML templates
4. Generates a single `build/index.html` presentation
5. Includes keyboard navigation and slide counter

## Prerequisites
The plugin must have dependencies installed (one-time):
```bash
cd ~/.claude/skills/uw-slides
pixi install
```

## Directory Structure Required
```
./
├── content/              # Markdown files (one per slide)
│   ├── 01-title.md
│   ├── 02-content.md
│   └── ...
├── order.txt             # Slide sequence
├── assets/               # Images (optional)
└── build/                # Output (created by renderer)
```

## Usage

When Claude invokes this skill, it will:
1. Check you're in a directory with `content/` folder
2. Run the renderer: `~/.claude/skills/uw-slides/skills/slide-renderer/render.sh`
3. Generate `build/index.html`
4. Report the output location

## Manual Usage
You can also run the renderer directly:
```bash
cd your-presentation-directory
~/.claude/skills/uw-slides/skills/slide-renderer/render.sh
```

## Available Layouts
See `LAYOUTS.md` for complete documentation:
- `title` — Title slide with UW branding
- `default` — Standard content slide
- `two-column` — Side-by-side content
- `comparison` — Before/after comparison
- `code` — Code snippets with syntax highlighting
- `transition` — Section dividers
- `image-bottom` — Content with large image
- `architecture` — Diagram-focused layout

## Output
- Single HTML file: `build/index.html`
- Self-contained (includes all CSS inline)
- Keyboard navigation: Arrow keys, Space, PageUp/Down
- Slide counter in bottom right
- Click anywhere to advance

## Troubleshooting

**"content directory not found"**
- Make sure you're in a presentation directory
- Must have a `content/` subdirectory with `.md` files

**"Module not found" errors**
- Run `pixi install` in the plugin directory
- Check that `.pixi/envs/default/` exists

**Slides don't render correctly**
- Check YAML frontmatter syntax (must start with `---`)
- Verify layout name matches available layouts
- Check for special syntax: `::left::`, `::right::`, `::note::`

## Implementation
Uses:
- **Jinja2** for template rendering
- **PyYAML** for frontmatter parsing  
- **Python Markdown** for content conversion
- **Pixi** for dependency management
