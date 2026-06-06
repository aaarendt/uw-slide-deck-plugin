# UW Slides Plugin

Create University of Washington branded presentations with any LLM using a fragment-based architecture.

## Features

- ✅ **LLM-agnostic:** Works with Claude, GPT, Gemini, Llama, etc.
- ✅ **Fragment-based:** Each slide is self-contained HTML with inline styles
- ✅ **Full creative freedom:** No rigid templates, LLM designs each slide
- ✅ **Easy reordering:** Edit order.txt and rebuild
- ✅ **UW brand compliant:** Design system documented in DESIGN.md
- ✅ **WCAG 2.1 AA accessible:** Built-in accessibility requirements
- ✅ **Simple build:** Bash script, no Python/Jinja2/parsing

## Quick Start

```bash
# Create new presentation
/uw-slides:new-deck my-presentation

# Request slides via conversation
"Create a title slide for a talk about climate modeling"

# Build and preview
cd my-presentation
./build.sh
open build/index.html
```

## Architecture

### Directory Structure

When you create a new presentation with `/uw-slides:new-deck`, you get:

```
presentation-name/
├── shared/
│   ├── header.html          # Design tokens, base styles
│   └── footer.html          # Navigation, closing tags
├── content/                 # Your slide fragments go here
│   ├── 01-title.html
│   ├── 02-overview.html
│   └── 03-conclusion.html
├── assets/
│   ├── images/
│   └── diagrams/
├── order.txt                # List of slides in sequence
├── build.sh                 # Concatenation script
└── README.md               # User instructions
```

### Fragment Pattern

Each slide is a complete HTML `<section>` with:
- Unique `data-slide` attribute
- Accessibility `aria-label`
- Content structure (any HTML)
- Inline scoped styles using attribute selector

```html
<section data-slide="01-title" aria-label="Title Slide" class="slide">
  <div><!-- content --></div>
  <style>
    section[data-slide="01-title"] {
      /* scoped styles - no conflicts with other slides */
      background: var(--uw-spirit-purple);
      padding: var(--space-20);
    }
  </style>
</section>
```

**Key pattern:** Use `section[data-slide="unique-id"]` for perfect CSS scoping. No class name conflicts, no cascade issues.

### Build Process

Simple concatenation via bash script:
```bash
# Reads order.txt line by line
cat shared/header.html > build/index.html
cat content/01-title.html >> build/index.html
cat content/02-overview.html >> build/index.html
cat shared/footer.html >> build/index.html
```

No templating, no parsing, no fragility. Just plain file concatenation.

### Workflow

1. **Scaffold:** Run `/uw-slides:new-deck presentation-name` to create directory structure
2. **Create slides:** Request slides one-by-one via conversation with your LLM
3. **Generate fragments:** LLM creates self-contained HTML sections following DESIGN.md
4. **Build:** Run `./build.sh` to concatenate into single HTML file
5. **Preview:** Open `build/index.html` in browser
6. **Reorder:** Edit `order.txt` and rebuild

## Design System

Comprehensive UW brand guidelines in **`design-system/DESIGN.md`**:
- Color palette with contrast ratios and PMS references
- Typography scale and patterns (Encode Sans, Open Sans)
- Layout and composition rules
- Component examples with complete code
- Accessibility requirements (WCAG 2.1 AA)
- Code implementation with design tokens
- Common slide layout patterns
- Pre-commit checklist

**Any LLM can read DESIGN.md** and generate brand-compliant slides. The documentation is written in prose format (not code-first) to be universally readable.

All slides automatically have access to design tokens:
```css
var(--uw-spirit-purple)  /* #4b2e83 */
var(--uw-spirit-gold)    /* #ffc700 */
var(--font-display)      /* Encode Sans */
var(--font-body)         /* Open Sans */
var(--space-8)           /* 32px */
```

## Skills

- **new-deck**: Scaffold new presentation with fragment architecture
- **accessibility-check**: WCAG 2.1 validation
- **design-review**: Brand compliance review
- **extract-to-markdown**: Convert slides to markdown outline

## Documentation

- **`design-system/DESIGN.md`** - Complete design system reference (5,500+ words)
- **`QUICKSTART.md`** - 5-minute tutorial
- `templates/examples/` - Example slide fragments
- `CONTRIBUTING.md` - How to contribute

## License

MIT
