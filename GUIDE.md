# UW Slides Plugin - Complete Guide

## Installation (One-Time)

Create a symlink so Claude Code can find this plugin:

```bash
ln -s /path/to/uw-slides-plugin ~/.claude/plugins/local/uw-slides
```

That's it! No dependencies to install. The plugin is now available in any Claude Code session.

## Creating Your First Presentation

### 1. Scaffold a New Deck

In Claude Code:

```
/uw-slides:new-deck my-climate-talk
```

This creates:
```
my-climate-talk/
├── shared/          # Header & footer templates (CSS variables, navigation)
│   ├── header.html
│   └── footer.html
├── content/         # Your slide HTML fragments (empty initially)
├── assets/
│   ├── images/
│   └── diagrams/
├── SLIDES.md        # Master planning document (defines order + notes)
├── build.sh         # Build script (concatenates fragments)
└── README.md        # Quick reference
```

### 2. Plan Your Presentation

Edit `SLIDES.md` with your slide ideas in any format you like:

```markdown
# Climate Data Analysis

Presentation for ESS conference, ~15 minutes

## 01-title
Title slide - Climate Data Analysis with Machine Learning
Presenter: [Your Name], University of Washington
Date: June 2026

## 02-motivation
Why we need better climate models
- Current limitations in traditional approaches
- Show impact diagram (workflow.png)
- Key message: accuracy vs speed tradeoff

## 03-approach
Our machine learning approach
Two-column layout:
- Left: traditional statistical methods (slow, limited)
- Right: our ML approach (fast, scalable)
Dark purple background for impact

## 04-results
Show the results with charts
- Accuracy improvement: 23%
- Speed improvement: 100x
- Include comparison chart

## 05-conclusion
Next steps and takeaways
- Checkmark list of action items
- Call to action for collaboration
```

**Format freedom:** Use bullet points, prose, notes to yourself - whatever makes sense. The LLM reads this to generate appropriate slides.

### 3. Generate Slides via Conversation

Ask Claude (or any LLM) to create slides based on your plan:

**You:** "Create slide 1 based on SLIDES.md"

**Claude will:**
1. Read SLIDES.md to understand your plan
2. Generate `content/01-title.html` with complete HTML and inline scoped styles
3. Confirm the slide was created

**You:** "Create slide 2 based on SLIDES.md"

Repeat for each slide. Each one is a self-contained HTML fragment with its own layout and styles.

### 4. Build and Preview

```bash
cd my-climate-talk
./build.sh
open build/index.html
```

Your presentation is now a single HTML file with keyboard navigation.

**Navigation:**
- Arrow keys, Space, PageUp/PageDown: Navigate slides
- Home/End: Jump to first/last slide
- Click anywhere: Advance to next slide
- Slide counter: Bottom right shows current/total

### 5. Iterate

**Edit content:**
- Update SLIDES.md with new notes
- Ask Claude: "Regenerate slide 3 based on the updated SLIDES.md"
- Rebuild: `./build.sh`

**Reorder slides:**
- Move `## slide-id` headings in SLIDES.md to desired order
- Rebuild: `./build.sh`

**Add new slides:**
- Add new `## slide-id` heading in SLIDES.md
- Ask Claude: "Generate slide 6 based on SLIDES.md"
- Rebuild: `./build.sh`

## How It Works

### Fragment-Based Architecture

```
Build process: header.html + slides (from SLIDES.md order) + footer.html = index.html
```

**Key concepts:**

1. **SLIDES.md** defines slide order via `## slide-id` headings
2. **HTML fragments** in `content/` are self-contained with inline scoped styles
3. **build.sh** extracts slide order from SLIDES.md and concatenates files
4. **CSS variables** from header.html provide UW brand design tokens
5. **No templating, no parsing** - just simple file concatenation

### Slide Fragment Pattern

Each slide follows this pattern:

```html
<section data-slide="03-approach" 
         aria-label="Slide 3: Our Approach"
         class="slide">

  <div class="content">
    <h1>Our Approach</h1>
    <p>Content goes here...</p>
  </div>

  <style>
    /* All styles scoped to this specific slide */
    section[data-slide="03-approach"] {
      background: var(--uw-spirit-purple);
      display: grid;
      grid-template-columns: 1fr 1fr;
      padding: 80px;
    }
    
    section[data-slide="03-approach"] h1 {
      font-family: var(--font-display);
      font-size: 56px;
      color: var(--uw-white);
    }
  </style>
</section>
```

**Scoped styles:** The `section[data-slide="..."]` selector ensures styles only apply to this slide - no conflicts, no cascade issues.

## Available CSS Variables (Design Tokens)

All slides have access to UW brand design tokens from `shared/header.html`:

**Colors:**
- `--uw-spirit-purple` (#4b2e83) - Primary brand color
- `--uw-husky-purple` (#32006e) - Darker variant
- `--uw-spirit-gold` (#ffc700) - Accent color
- `--uw-husky-gold-web` (#e8e3d3) - Light cream
- `--uw-heritage-gold` (#85754d) - Text on light
- `--uw-white`, `--uw-black`, `--uw-gray-90`, etc.

**Typography:**
- `--font-display` (Encode Sans) - For headlines
- `--font-display-wide` (Encode Sans Wide)
- `--font-display-compressed` (Encode Sans Compressed)
- `--font-body` (Open Sans) - For body text

**Spacing:** (8px grid)
- `--space-1` (8px) through `--space-12` (96px)

**Example usage:**
```css
section[data-slide="my-slide"] {
  background: var(--uw-spirit-purple);
  padding: var(--space-8);
}

section[data-slide="my-slide"] h1 {
  font-family: var(--font-display);
  color: var(--uw-spirit-gold);
}
```

## Skills

### /uw-slides:new-deck
Scaffold a new presentation with fragment-based structure.

### /uw-slides:accessibility-check
Validate WCAG 2.1 Level AA compliance:
- Contrast ratios (4.5:1 minimum)
- Font sizes (24px minimum)
- Alt text on images
- Semantic HTML
- ARIA labels

### /uw-slides:design-review
Review UW brand compliance:
- Color usage
- Typography
- Layout patterns
- Logo usage

### /uw-slides:extract-to-markdown
Extract content from existing HTML presentations to create a SLIDES.md outline.

## Troubleshooting

### "SLIDES.md not found"

You're not in a presentation directory. Check:
- Current directory has `SLIDES.md`
- File contains `## slide-id` headings

### Slides don't render

Check that:
- HTML files exist in `content/` directory
- Filenames match `## slide-id` headings in SLIDES.md (without .html extension)
- Each `<section>` has `class="slide"` attribute
- Build completed without errors

### Wrong slide order

The order is determined by `## slide-id` sequence in SLIDES.md (top to bottom), not by filename. Edit SLIDES.md to reorder.

### Images not showing

Image paths are relative to `build/index.html`:
```html
<!-- From build/index.html, go up to deck root, then into assets -->
<img src="../assets/images/photo.jpg" alt="Description">
```

### Fonts not loading

Font paths in `shared/header.html` point to the plugin directory:
```
../../design-system/fonts/EncodeSansNormal-900-Black.ttf
```

This assumes the plugin is at `~/.claude/plugins/local/uw-slides/`. If installed elsewhere, update font paths in `shared/header.html`.

### Build script fails

Common issues:
- Missing `shared/header.html` or `shared/footer.html`
- SLIDES.md has no `## slide-id` headings
- Permissions: make sure `build.sh` is executable (`chmod +x build.sh`)

## Customization

### Modifying Design Tokens

Edit `shared/header.html` in your presentation to change:
- Colors (`:root` CSS variables)
- Spacing scale
- Typography settings

These changes only affect that presentation.

### Custom Layouts

Ask your LLM to generate slides with any layout:
- Grid layouts
- Flexbox layouts
- Absolute positioning
- Multi-column
- Full-bleed images
- Mixed layouts

**No rigid templates** - the LLM designs freely within UW brand constraints.

### Global Plugin Changes

To change defaults for all new presentations, edit:
- `~/.claude/plugins/local/uw-slides/templates/shared/header.html`
- `~/.claude/plugins/local/uw-slides/templates/shared/footer.html`

These are copied when creating new decks with `/uw-slides:new-deck`.

## Tips & Best Practices

**Planning in SLIDES.md:**
- Start with slide ideas before asking LLM to generate HTML
- Use section headings for major transitions
- Include speaker notes and key messages
- Reference image filenames so LLM knows what assets to use

**Working with LLMs:**
- Be specific: "Create a two-column comparison slide with purple background"
- Reference SLIDES.md: "Generate slide 3 based on SLIDES.md section"
- Iterate: "Make the title larger and change to gold color"
- Ask for variants: "Show me 3 different layout options for this slide"

**Accessibility:**
- Always include alt text for images
- Use semantic HTML (`<h1>`, `<p>`, `<ul>`, etc.)
- Test keyboard navigation
- Check contrast ratios (use `/uw-slides:accessibility-check`)

**Version Control:**
- Commit `SLIDES.md` and `content/*.html` files
- Add `build/` to `.gitignore` (already done)
- Clean diffs: one file per slide change

## Architecture Summary

```
uw-slides/
├── templates/
│   ├── shared/              # Copied to new presentations
│   │   ├── header.html      # Design tokens, fonts, base styles
│   │   └── footer.html      # Navigation JavaScript
│   ├── examples/            # Example slide fragments
│   │   ├── 01-title-example.html
│   │   └── 02-comparison-example.html
│   ├── build.sh             # Build script template
│   └── SLIDES.md            # Planning document template
├── design-system/           # UW design system
│   ├── DESIGN.md            # Comprehensive design guide (5,500+ words)
│   ├── fonts/               # Encode Sans font files (45 variants: 5 widths × 9 weights)
│   └── colors_and_type.css  # Design tokens and @font-face declarations
└── skills/                  # Claude Code skills
    ├── new-deck/
    ├── accessibility-check/
    ├── design-review/
    └── extract-to-markdown/
```

## No Dependencies Required

This plugin requires only:
- **bash** (standard on Linux/macOS/WSL)
- **browser** (to view presentations)
- **LLM** (to generate slides)

No Python, no Node.js, no package managers, no build tools.

## License

MIT - See LICENSE file
