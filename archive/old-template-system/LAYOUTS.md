# UW Slides Layout Reference

Complete guide to all available slide layouts in the UW Slides plugin.

## Quick Reference

| Layout | Use Case | Theme Options |
|--------|----------|---------------|
| `title` | Opening/title slide | purple (default) |
| `default` | Standard content | light, dark |
| `two-column` | Side-by-side content | light (default), dark |
| `comparison` | Before/after, pros/cons | panel-based |
| `code` | Code snippets | dark (default), light |
| `architecture` | System diagrams | light, dark |
| `transition` | Section dividers | purple (default), dark, gold |
| `image-bottom` | Content + large image | light (default), dark |

---

## Layout Details

### 1. Title Slide

**Use for:** Opening slide, title page  
**Layout:** `title`

```yaml
---
layout: title
eyebrow: "Optional small label"
presenter: "Your Name"
partner_logos:
  - filename: "partner-logo.png"
    alt: "Partner organization logo"
---

# Main Presentation Title

## Subtitle or tagline
```

**Features:**
- Large UW W logo at top
- Centered title with UW branding
- Optional presenter name
- Optional partner logos at bottom
- Purple background with gold accent bar

---

### 2. Default/Standard Slide

**Use for:** Standard content, bullet points, general text  
**Layout:** `default` (or omit layout field)

```yaml
---
title: "Slide Title"
eyebrow: "OPTIONAL LABEL"
theme: light  # or dark
accent_bar: top  # or left
---

## Main content

- Bullet point one
- Bullet point two
- Bullet point three

Additional paragraph text.
```

**Theme options:**
- `light` (default): White background, purple text
- `dark`: Purple background, white/cream text

---

### 3. Two-Column Layout

**Use for:** Comparing concepts, parallel information, side-by-side lists  
**Layout:** `two-column`

```yaml
---
layout: two-column
title: "Comparing Approaches"
theme: light  # or dark
---

::left::
## Traditional Method
- Manual processes
- Time-intensive
- Higher error rate

::right::
## AI-Assisted Method
- Automated workflows
- Faster iteration
- Built-in validation
```

**Features:**
- Equal-width columns with vertical gold divider
- Optional headings for each column
- Supports bullet lists, text, images in each column

**Special syntax:**
- `::left::` marks beginning of left column content
- `::right::` marks beginning of right column content

---

### 4. Comparison Slide

**Use for:** Before/after, Option A vs B, pros/cons  
**Layout:** `comparison`

```yaml
---
layout: comparison
title: "Before and After"
left_label: "Before"
right_label: "After"
left_theme: purple
right_theme: white
divider_label: "→"  # optional
---

::left::
- Manual data entry
- Error-prone
- Time consuming

::right::
- Automated pipeline
- Validated inputs
- 10x faster
```

**Panel theme options:**
- `purple`: Purple background, white text
- `gold`: Gold background, dark purple text
- `white`: White background, dark text (default for right)

**Features:**
- Distinct colored panels for each side
- Optional divider label (e.g., "vs", "→")
- Rounded panel design with themed borders

---

### 5. Code Slide

**Use for:** Displaying code snippets, configuration files, commands  
**Layout:** `code`

```yaml
---
layout: code
title: "Implementation Example"
eyebrow: "PYTHON"  # Language label
language: "python"  # Shown on badge
theme: dark  # or light
accent_bar: left  # default for code slides
---

```python
def process_data(input_file):
    """Load and validate dataset."""
    data = pd.read_csv(input_file)
    return data.dropna()
```

Optional caption text explaining the code.
```

**Features:**
- Syntax-friendly dark background
- Language badge at top of code block
- Gold left border on code block
- Optional caption below code
- Monospace font optimized for readability

**Notes:**
- HTML special characters (`<`, `>`, `&`) are automatically escaped
- Use triple backticks for code blocks in markdown

---

### 6. Architecture Slide

**Use for:** System diagrams, flowcharts, architecture overviews  
**Layout:** `architecture`

```yaml
---
layout: architecture
title: "System Architecture"
eyebrow: "OVERVIEW"
theme: light  # or dark
---

![System architecture diagram](../assets/diagrams/architecture.svg)

## Key Components

- API Gateway
- Processing Pipeline
- Data Store
```

**Features:**
- Optimized for large diagrams
- Supports both raster and vector graphics
- Can combine diagram with explanatory text
- Diagram-first layout with text below or beside

---

### 7. Transition Slide

**Use for:** Section dividers, chapter breaks, topic transitions  
**Layout:** `transition`

```yaml
---
layout: transition
section_number: "02"  # Large decorative number
section_label: "PART TWO"  # Small uppercase label
title: "Implementation"
subtitle: "From theory to practice"
theme: purple  # or dark, or gold
---
```

**Theme options:**
- `purple` (default): Spirit purple background
- `dark`: Husky purple (darker) background
- `gold`: Gold background with dark purple text

**Features:**
- Full-screen bold design
- Large decorative section number (optional)
- Uppercase section label (optional)
- Extra-large title text
- Lighter subtitle text
- Gold accent bars top and bottom

---

### 8. Image-Bottom Layout

**Use for:** Content with supporting image, photo with context  
**Layout:** `image-bottom`

```yaml
---
layout: image-bottom
title: "Research Site"
eyebrow: "LOCATION"
theme: light  # or dark
image_src: "../assets/images/field-site.jpg"
image_alt: "Aerial view of the research field site"
caption: "Mt. Rainier study area, elevation 1,800m"
---

## Study Location

- 50 hectares
- Mixed forest ecosystem
- Continuous monitoring since 2020

![Research site](../assets/images/field-site.jpg)
```

**Features:**
- Content area at top (title, bullets, text)
- Large image region at bottom
- Image scales to fill available space
- Optional caption below image
- Responsive to different image aspect ratios

**Accessibility:**
- `image_alt` is required for screen readers
- Caption provides additional context

---

## Common Frontmatter Fields

### Required
- `title`: Main slide heading

### Optional (all layouts)
- `layout`: Template name (defaults to `default` if omitted)
- `eyebrow`: Small uppercase label above title
- `theme`: `light` or `dark` (varies by layout)
- `accent_bar`: `top` or `left` (gold bar position)
- `slide_id`: Unique identifier (auto-generated from filename if omitted)
- `background`: Color name (for advanced use)

### Slide Organization
- `section`: Logical grouping for related slides
- `duration_min`: Estimated speaking time (for planning)
- `presenter`: Who presents this slide

### Accessibility
- `alt_texts`: Dictionary mapping image filenames to descriptions
  ```yaml
  alt_texts:
    diagram.png: "Data flow showing three processing stages"
    photo.jpg: "Team members collaborating at whiteboard"
  ```

---

## Special Markdown Syntax

### Column Dividers
For `two-column` and `comparison` layouts:

```markdown
::left::
Left column content here

::right::
Right column content here
```

### Speaker Notes
In any slide (not rendered, for presenter reference):

```markdown
::note::
Remember to emphasize the time savings here.
Mention the Smith et al. study if asked.
```

### Images
Standard markdown syntax:

```markdown
![Alt text](../assets/images/filename.png)
```

For accessibility, also add to frontmatter:
```yaml
alt_texts:
  filename.png: "Detailed description for screen readers"
```

---

## Design Guidelines

### Font Sizes
- Slide title: 56-86px (varies by layout)
- Body text: 28-34px
- Minimum: 24px (WCAG 2.1 AA compliance)

### Colors
All layouts use UW brand colors:
- **Spirit Purple** (`#4b2e83`): Primary brand color
- **Husky Purple** (`#32006e`): Darker accent
- **Spirit Gold** (`#ffc700`): Accent bars, highlights
- **Heritage Gold** (`#85754d`): Text on light backgrounds
- **Husky Gold Web** (`#e8e3d3`): Cream, text on dark backgrounds

### Accessibility
All templates meet **WCAG 2.1 Level AA** requirements:
- Contrast ratios: 4.5:1 minimum for text
- All images require alt text
- ARIA labels on sections
- Keyboard navigation support

---

## Tips and Best Practices

### Choosing a Layout

1. **Start with title slide** - Every deck should begin with `layout: title`
2. **Use transitions between sections** - Break up long presentations
3. **Match layout to content type:**
   - Lists and text → `default`
   - Comparisons → `comparison` or `two-column`
   - Code → `code`
   - Diagrams → `architecture` or `image-bottom`
4. **Don't overuse special layouts** - Most slides should be `default` or `two-column`

### Content Guidelines

- **One main idea per slide** - Keep it focused
- **Limit bullets to 3-5 per slide** - Avoid text walls
- **Use high-contrast images** - Especially for `image-bottom`
- **Test code readability** - Use `code` layout for snippets >3 lines
- **Add speaker notes** - Use `::note::` sections for presentation guidance

### Accessibility Checklist

- [ ] All images have alt text
- [ ] Color is not the only indicator (use labels + color)
- [ ] Text size is ≥24px
- [ ] Contrast ratios meet WCAG AA (use `/uw-slides:accessibility-check`)
- [ ] Slide titles are descriptive

---

## Examples

See the `examples/` directory for complete example decks using each layout:
- `examples/complete-deck/` - All layouts demonstrated
- `examples/research-talk/` - Academic presentation example
- `examples/tech-overview/` - Technical presentation with code

---

## Related Documentation

- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [README.md](README.md) - Plugin overview
- [design-systems/uw-brand/DESIGN.md](design-systems/uw-brand/DESIGN.md) - UW brand specifications
- [references/accessibility-requirements.md](references/accessibility-requirements.md) - WCAG compliance details
- [references/markdown-schema.md](references/markdown-schema.md) - Complete frontmatter reference

---

## Template Source Files

Layout templates are in `design-systems/uw-brand/templates/`:
- `title.html`
- `two-column.html`
- `comparison.html`
- `code.html`
- `architecture.html`
- `transition.html`
- `image-bottom.html`

These are Jinja2 templates used by the renderer. For most users, the markdown syntax documented above is all you need.
