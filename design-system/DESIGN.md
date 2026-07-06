# University of Washington Design System

> Category: Education & Academia  
> Official UW brand guidelines, WCAG 2.1 AA compliant

## 1. Visual Theme & Atmosphere

The University of Washington's visual identity is built on tradition and academic excellence, expressed through the bold pairing of Spirit Purple and Spirit Gold. The design system emphasizes clarity, accessibility, and institutional pride while maintaining a contemporary, professional aesthetic suitable for research presentations, educational materials, and public engagement.

The UW brand represents rigor and trustworthiness. Visual designs should feel authoritative yet approachable, leveraging strong typography (Encode Sans Black at 900 weight) for commanding headlines paired with the highly readable Open Sans for body content. The color palette is deliberately restrained—Spirit Purple dominates, Spirit Gold accents strategically—allowing content to shine without visual noise.

This design system prioritizes accessibility as a core requirement, not an afterthought. Every guideline in this document ensures WCAG 2.1 Level AA compliance, with minimum 24px font sizes for presentations, 4.5:1 contrast ratios, and semantic HTML structure. The goal is to create presentations that are both visually striking and universally accessible.

**Key Characteristics:**
- Spirit Purple (#4b2e83) as primary brand color
- Spirit Gold (#ffc700) for accents and emphasis
- Encode Sans (Black weight 900) for impactful headlines
- Open Sans for readable body text
- WCAG 2.1 Level AA compliant (4.5:1 contrast minimum)
- Minimum 24px font size for presentations
- Clean, academic aesthetic without excessive decoration

## 2. Color Palette & Roles

### Primary Brand Colors

- **Spirit Purple** (`#4b2e83`, PMS 266): Primary brand color. Use for headings, backgrounds, and primary UI elements. The most recognizable UW color. This is the go-to purple for nearly all UW materials. It conveys institutional identity and should dominate the visual hierarchy. Most-used digital purple across all UW digital properties.
  
- **Husky Purple** (`#32006e`, PMS 2685): Darker variant for depth and contrast. Use for: darker backgrounds, text on light surfaces, shadows, and situations requiring greater visual weight. This creates sophisticated depth when paired with Spirit Purple. The darkest purple in the palette.
  
- **Spirit Gold** (`#ffc700`): Primary accent color. Bright gold for highlights. Use for: accent bars, highlights, interactive elements, calls-to-action. **Critical: Never use as body text**—it fails contrast requirements on both white and purple backgrounds. Reserve for pure accent purposes: thin bars, bullets, underlines, and emphasis elements.
  
- **Husky Gold Web** (`#e8e3d3`): Light cream tone. Use for: text on purple backgrounds, subtle surface tinting, secondary backgrounds. This is the safe "gold" for text—it meets contrast requirements when Spirit Gold doesn't. Use it as the light text color on dark purple slides. Digital background color optimized for screens.
  
- **Husky Gold** (`#b7a57a`): Warm gold, primarily for print materials. Use sparingly in digital presentations—Husky Gold Web is preferred for screens.
  
- **Heritage Gold** (`#85754d`): Deep muted gold. Use for: text on light backgrounds, sophisticated accents, de-emphasized elements. This earthy gold works for body text on white when you want gold-toned content that remains readable.

### Neutrals

- **White** (`#ffffff`): Surface backgrounds, text on dark backgrounds. The default light surface color for content slides.
- **Black** (`#000000`): Strong text on light backgrounds, rarely used pure. Prefer Gray 90 for most text to reduce harshness.
- **Gray 90** (`#1a1a1a`): Near-black for body text on white. This is the standard text color—softer than pure black while maintaining excellent contrast (15.8:1 ratio).
- **Gray 70** (`#4d4d4d`): Secondary text, captions, metadata. Use when content needs visible de-emphasis.
- **Gray 50** (`#808080`): Mid-gray for borders and subtle UI elements.
- **Gray 30** (`#b3b3b3`): Disabled states, borders, dividers. Light enough for subtle separation without drawing attention.
- **Gray 10** (`#e6e6e6`): Very light gray for subtle backgrounds and surfaces.
- **Warm Cream** (`#e8d3a2`): Warmer alternative to Husky Gold Web, from official PowerPoint theme.

### Accent Colors (Use Sparingly)

These colors are available but should be used rarely and intentionally, primarily for data visualization or to indicate specific states:

- **Accent Green** (`#aadb1e`): Success states, growth indicators, positive metrics
- **Accent Teal** (`#2ad2c9`): Interactive elements, links (alternative to purple)
- **Accent Pink** (`#e93cac`): Rare highlight, avoid in formal contexts
- **Accent Lavender** (`#c5b4e3`): Soft accent, data visualization pastels

**Guidance:** Most slides should use only Purple, Gold, and neutrals. Introduce accent colors only when semantic meaning requires it (e.g., green for positive outcomes, teal for interactive states). **Accent colors should comprise ≤15% of any design** to maintain brand consistency and visual clarity.

## 3. Typography Rules

### Font Families

**Encode Sans** (Display)
- Source: Google Fonts or local files (45 font variations installed across five width families)
- Weights available: 100 (Thin) → 900 (Black) for each width
- Primary weight: **900 (Black)** for headlines
- Usage: All headings, slide titles, impactful statements
- Character: Geometric, bold, commanding, uppercase-friendly
- Never use below 20px

**Encode Sans Width Variants:**

1. **Encode Sans Wide** - Expanded width (208KB per weight)
   - **Use for:** Extra-large impact titles, hero headlines on title slides
   - **Character:** Maximum visual presence, demands attention
   - **Example:** Opening slide main title, section divider headlines

2. **Encode Sans** (Normal) - Standard width (205KB per weight)
   - **Use for:** Default choice for all headings
   - **Character:** Balanced proportions, most versatile
   - **Example:** Standard slide titles (56px), subtitles (36-48px)

3. **Encode Sans Narrow** - Slightly condensed (205KB per weight)
   - **Use for:** Longer headlines that need to fit
   - **Character:** Compact without feeling cramped
   - **Example:** Slide titles with longer text (~10+ words)

4. **Encode Sans Condensed** - More condensed (205KB per weight)
   - **Use for:** Dense information displays, data-heavy slides
   - **Character:** Tight spacing, efficient use of horizontal space
   - **Example:** Table headers, chart labels, metadata

5. **Encode Sans Compressed** - Maximum condensation (196KB per weight)
   - **Use for:** Extreme space constraints, specialized layouts
   - **Character:** Very tight, use sparingly
   - **Example:** Dense technical slides, code annotations

**Selection Guide:**
- **Default:** Always start with Normal
- **Hero moments:** Use Wide for title slides and major section breaks
- **Long text:** Use Narrow when headlines are >8 words
- **Dense data:** Use Condensed for tables, charts, technical content
- **Special cases only:** Compressed is for rare situations with extreme space limits

**When to use:** Encode Sans is exclusively for headings and display text. Its extreme black weight (900) creates the visual punch that defines UW presentations. Always uppercase for maximum impact on title slides.

**Open Sans** (Body)
- Source: Google Fonts
- Weights available: 300 (Light), 400 (Regular), 600 (Semibold), 700 (Bold)
- Primary weights: **400 (Regular)** for body, **600 (Semibold)** for emphasis
- Usage: Body text, captions, labels, UI elements, lists
- Character: Highly readable, neutral, professional, humanist sans-serif
- Minimum size: 24px in presentations (WCAG requirement)
- **When to use:** Open Sans is for everything that isn't a headline. Its high x-height and open apertures ensure readability even at distance. Use 400 for paragraphs, 600 for emphasized phrases or list items that need weight.

### Typography Scale (Presentations)

This scale is optimized for 1920×1080 presentations viewed from 10+ feet:

| Element | Font | Size | Weight | Line Height | Letter Spacing | Use Case |
|---------|------|------|--------|-------------|----------------|----------|
| Hero Title | Encode Sans | 72-86px | 900 | 1.0 | -0.02em | Opening slides, section dividers |
| Slide Title | Encode Sans | 56px | 800 | 1.1 | -0.01em | Standard slide headings |
| Subtitle | Encode Sans | 36-48px | 700 | 1.2 | normal | Secondary headlines |
| Body Large | Open Sans | 32-34px | 400 | 1.5 | normal | Main content, lists |
| Body | Open Sans | 28px | 400 | 1.6 | normal | Secondary content |
| Caption | Open Sans | 24px | 600 | 1.4 | normal | Metadata, sources, notes |
| Minimum | — | 24px | — | — | — | WCAG 2.1 AA requirement |

**Scale Rationale:**
- **Hero titles (72-86px):** Must be readable from the back of a large room. Use on opening slides and major section transitions.
- **Slide titles (56px):** The standard heading size. Every content slide should have one h1 at this size.
- **Body (28-34px):** Significantly larger than web body text. Presentation text must work at distance.
- **Caption (24px):** The absolute minimum. Use only for citations, figure labels, and metadata.

### Typography Patterns

**Slide Title Pattern:**
```css
h1 {
  font-family: 'Encode Sans', sans-serif;
  font-size: 56px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.01em;
  text-transform: uppercase;
  color: #4b2e83; /* Spirit Purple */
}
```

**Why uppercase:** Encode Sans Black is designed for uppercase display. Lowercase loses impact.

**Body Text Pattern:**
```css
p, li {
  font-family: 'Open Sans', sans-serif;
  font-size: 28px;
  font-weight: 400;
  line-height: 1.6;
  color: #1a1a1a; /* Gray 90 */
}
```

**Why 1.6 line-height:** Presentations need generous vertical spacing for legibility at distance. Tight leading (1.2-1.4) works on screens, fails in rooms.

**Emphasis Pattern:**
```css
strong, .emphasis {
  font-weight: 600; /* Open Sans Semibold */
  color: #4b2e83; /* Spirit Purple for extra emphasis */
}
```

**When to emphasize:** Use sparingly. If everything is bold, nothing is. Reserve for 1-2 key phrases per slide.

## 4. Layout & Composition

### Presentation Layouts

**Grid System:**
- Base unit: 8px
- Padding: 60-80px from edges (provides safety margin for projector cutoff)
- Content area: Center 80% of slide (safe zone)
- Safe zone: 5% margin on all sides (ensures nothing critical near edges)

**Why generous padding:** Projectors often cut off screen edges. The 60-80px padding ensures no content is lost. Additionally, large empty margins direct focus to the content area and prevent slides from feeling cramped.

**Common Patterns:**

1. **Centered Title Slide**
   - Vertical center alignment
   - UW logo at top (120px height)
   - Title + subtitle + metadata stack
   - Gold accent bar at top (8px)
   - **Use for:** Opening slide, section dividers
   - **Why centered:** Ceremony and symmetry signal importance. Opening slides should feel formal.

2. **Content with Sidebar**
   - 2:1 or 3:2 grid columns
   - Main content left, supporting right
   - Minimum 40px gap
   - **Use for:** Slide with primary narrative plus supporting data/image
   - **Why asymmetric:** Creates visual hierarchy. Left column (larger) is read first.

3. **Two-Column Equal**
   - 1:1 grid columns
   - Vertical gold divider (2px)
   - 60px gap between columns
   - **Use for:** Comparisons, before/after, parallel concepts
   - **Why equal columns:** Suggests equivalence or contrast, not hierarchy.

4. **Full-Bleed Image with Text**
   - Image as background or 50% split
   - Ensure text contrast (overlay if needed)
   - Minimum 4.5:1 ratio
   - **Use for:** High-impact visual moments, data visualization
   - **Why full-bleed:** Maximizes emotional impact of imagery. Requires careful text contrast management—use overlay scrims (semi-transparent purple or black) if needed.

### Spacing Scale

The spacing system uses a 4px base unit (with common 8px increments) to create visual rhythm:

```css
--space-1: 4px;    /* Minimal spacing, tight elements */
--space-2: 8px;    /* Base unit, tight layouts */
--space-3: 12px;   /* Small gaps */
--space-4: 16px;   /* Standard spacing between related elements */
--space-5: 20px;   /* Small section spacing */
--space-6: 24px;   /* Medium spacing */
--space-8: 32px;   /* Large spacing between sections */
--space-10: 40px;  /* Extra-large spacing */
--space-12: 48px;  /* Section padding */
--space-16: 64px;  /* Large section padding */
--space-20: 80px;  /* Slide margins, outer padding */
```

**Usage:**
- Between elements (e.g., heading to paragraph): `--space-4` (16px) to `--space-6` (24px)
- Between list items: `--space-4` (16px)
- Section padding (e.g., content block padding): `--space-8` (32px) to `--space-12` (48px)
- Slide margins (outer padding): `--space-16` (64px) to `--space-20` (80px)
- Tight elements (bullets, badges): `--space-2` (8px) to `--space-3` (12px)

**Spacing Philosophy:** Use the 4px/8px base unit consistently. Avoid arbitrary values (e.g., 35px, 47px). The rhythm created by the mathematical scale makes layouts feel intentional and harmonious.

## 5. Components & Patterns

### Accent Bar

Accent bars are thin gold lines that add visual structure without overwhelming content.

**Horizontal (Top):**
```html
<div class="accent-bar-top"></div>

<style>
.accent-bar-top {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 8px;
  background: #ffc700; /* Spirit Gold */
}
</style>
```

**Vertical (Left):**
```html
<div class="accent-bar-left"></div>

<style>
.accent-bar-left {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 8px;
  background: #ffc700; /* Spirit Gold */
}
</style>
```

**When to use:** Accent bars add polish and reinforce the UW brand. Use on slides that would otherwise feel plain. Don't use on every slide—strategic placement maintains impact.

### Logo Usage

**UW W Mark:**
- File: `W-Logo_Purple_RGB.png`
- On light backgrounds: Purple version
- On dark backgrounds: White version (use CSS filter: `brightness(0) invert(1)`)
- Minimum height: 80px (below this, details become unclear)
- Typical height: 120px
- Clear space: Equal to height of "W" on all sides (ensures logo isn't crowded)

**When to show the logo:**
- Always on the title slide
- Optional on content slides (typically not needed once established)
- Always on the final slide

**Logo placement:**
- Title slide: Top center or top left
- Content slides: Top left corner (small, ~80px) or omit

### Bullet Lists

**Standard Pattern:**
```html
<ul>
  <li>List item one</li>
  <li>List item two</li>
</ul>

<style>
ul {
  list-style: none;
  padding: 0;
}

li {
  font-size: 28px;
  line-height: 1.6;
  margin-bottom: 16px;
  padding-left: 36px;
  position: relative;
}

li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #ffc700; /* Spirit Gold bullet */
  font-weight: 700;
  font-size: 32px;
}
</style>
```

**Why gold bullets:** The gold bullet is a UW signature. It adds brand presence without distracting from content. The bullet is slightly larger than the text (32px vs 28px) to ensure visibility.

**List guidelines:**
- 3-5 items maximum per slide
- Each item should be one line (two lines maximum)
- Parallel structure (all phrases or all sentences)
- Consider using a heading above the list to provide context

## 6. Accessibility Requirements (WCAG 2.1 Level AA)

Accessibility is not optional—it's a requirement for all UW presentations. All work must comply with the **University of Washington Digital Accessibility Policy (APS 9.0)** and align with the ADA Digital Accessibility Initiative. These guidelines ensure your slides work for everyone, including people with visual impairments, color blindness, and those using assistive technology.

### Text Contrast

**Required ratios per WCAG 2.1 Level AA:**
- Body text (< 18pt / ~24px): 4.5:1 minimum
- Large text (≥ 18pt / ~24px, or 14pt bold): 3:1 minimum (but we use 4.5:1 for consistency)
- **Graphical elements and UI components**: 3:1 contrast ratio for interactive elements, focus indicators, and meaningful graphics

**Approved combinations:**

| Foreground | Background | Ratio | Status |
|------------|------------|-------|--------|
| Spirit Purple (#4b2e83) | White (#ffffff) | 8.6:1 | ✓ Excellent |
| White (#ffffff) | Spirit Purple (#4b2e83) | 8.6:1 | ✓ Excellent |
| Gray 90 (#1a1a1a) | White (#ffffff) | 15.8:1 | ✓ Excellent |
| Heritage Gold (#85754d) | White (#ffffff) | 4.7:1 | ✓ Pass |
| Husky Gold Web (#e8e3d3) | Spirit Purple (#4b2e83) | 4.9:1 | ✓ Pass |

**Failing combinations (never use):**

| Foreground | Background | Ratio | Status |
|------------|------------|-------|--------|
| Spirit Gold (#ffc700) | White | 1.9:1 | ✗ Fail |
| Spirit Gold | Spirit Purple | 2.8:1 | ✗ Fail |
| Gray 30 | White | 2.9:1 | ✗ Fail |

**How to test:** 
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Browser DevTools contrast tools (Chrome/Edge/Firefox built-in)
- WAVE Browser Extension: https://wave.webaim.org/extension/
- axe DevTools: https://www.deque.com/axe/devtools/

**Why this matters:** Low contrast makes text unreadable for people with low vision, color blindness, or when viewing in bright rooms (common in conferences).

**Critical rule: Do not rely on color alone** to convey information. Always combine color with text labels, icons, or patterns.

### Font Sizes

- **Minimum:** 24px for all text in presentations
- **Recommended:** 28px for body text, 32px+ for emphasis
- **Headings:** 56px minimum for slide titles

**Why 24px minimum:** WCAG 2.1 defines "large text" as 24px or larger. At this size, the 3:1 contrast requirement applies instead of 4.5:1. However, we maintain 4.5:1 regardless because presentations are viewed at distance.

### Semantic HTML

Use semantic HTML elements to ensure screen readers and assistive technology can understand your content structure:

```html
<section aria-label="Slide title here">
  <h1>Primary heading</h1>
  <h2>Secondary heading</h2>
  <p>Paragraph text</p>
  <ul>
    <li>List items</li>
  </ul>
</section>
```

**Required:**
- Use `<h1>` for slide titles, `<h2>` for subsections (don't skip levels)
- Use `<p>` for paragraphs, not `<div>`
- Use `<ul>/<ol>` for lists, not manual line breaks
- Use `<section>` with `aria-label` for each slide
- **Page language**: Include `lang="en"` attribute on `<html>` element
- **Landmarks**: Use semantic HTML5 elements (`<section>`, `<nav>`, `<main>`) or ARIA landmarks
- **ARIA labels**: Use `role`, `aria-label`, `aria-live` appropriately for dynamic content

**Why semantic HTML:** Screen readers use HTML structure to navigate content. A `<div>` with styled text isn't a heading to a screen reader—it's just text. Semantic HTML makes content accessible and machine-readable.

**Example of proper structure:**
```html
<section data-slide="01-intro" aria-label="Introduction: Project Overview" role="region">
  <h1>Project Overview</h1>
  <h2>Key Objectives</h2>
  <ul>
    <li>First objective</li>
    <li>Second objective</li>
  </ul>
</section>
```

### Images

All images must have:
- `alt` attribute with descriptive text
- Exception: Decorative images use `alt=""`
- Complex images (charts, diagrams): Consider additional caption or `aria-describedby`

**Alt text guidelines:**
- Describe what the image conveys, not what it looks like
- Keep it concise (1-2 sentences)
- If the image is complex (e.g., a chart), provide a text summary nearby

**Example:**
```html
<!-- Good: Descriptive alt text -->
<img src="chart.png" alt="Bar chart showing 40% increase in student enrollment from 2020 to 2025">

<!-- Bad: Non-descriptive -->
<img src="chart.png" alt="Chart">

<!-- Decorative: Empty alt -->
<img src="divider.png" alt="">

<!-- Complex image: Use aria-describedby for extended description -->
<img src="complex-diagram.png" 
     alt="System architecture diagram" 
     aria-describedby="diagram-description">
<p id="diagram-description" class="sr-only">
  Detailed description: The diagram shows three layers...
</p>
```

**Link text guidelines:**
- Links must be meaningful out of context
- Avoid "click here", "read more", "learn more" without context
- Good: "Read the accessibility guidelines"
- Bad: "Click here for guidelines"

### Keyboard Navigation

**All interactive elements must be:**
- Focusable with Tab key
- Activatable with Enter or Space
- Visible focus indicator (2px outline minimum, 3:1 contrast ratio)
- **Logical tab order** following visual layout
- **No keyboard traps** - users must be able to navigate away from any element

**For presentations:** The navigation JavaScript (in footer.html) supports full keyboard navigation:
- **Arrow Right/Left**: Previous/next slide
- **Space**: Next slide
- **Page Down/Up**: Next/previous slide
- **Home**: Jump to first slide
- **End**: Jump to last slide

**Focus indicators:**
```css
button:focus,
a:focus {
  outline: 2px solid #ffc700; /* Spirit Gold */
  outline-offset: 2px;
}

/* Ensure focus indicator meets 3:1 contrast with background */
*:focus {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

## 7. Presentation-Specific Guidelines

### Slide Types

**Title Slide:**
- Spirit Purple background
- White or Husky Gold Web text
- UW W logo (white-filtered)
- Gold accent bar at top
- Centered layout
- Presenter info at bottom
- **Purpose:** Opening ceremony. Sets tone and establishes credibility.

**Content Slide (Light Theme):**
- White background
- Gray 90 text
- Spirit Purple headings
- Optional gold accent bar (top or left)
- Flexible layout
- **Purpose:** Default slide type. Use for most content.

**Content Slide (Dark Theme):**
- Spirit Purple or Husky Purple background
- White headings
- Husky Gold Web body text
- Gold accent bar
- Use sparingly for emphasis
- **Purpose:** Visual break, high-impact moments. Don't overuse—dark slides can be fatiguing.

**Transition/Section Slide:**
- Full-bleed Spirit Purple
- Large white text (72-86px)
- Minimal content (just the section name)
- Gold bars top and bottom
- **Purpose:** Signals major topic shift. The visual equivalent of a chapter heading.

### Animation & Motion

Presentation animations should be subtle and purposeful. Avoid distractions.

**Allowed:**
- Slide transitions: Fade or cut (no swoops/zooms)
- Duration: 150-300ms
  - Fast transitions: 150ms for micro-interactions
  - Normal transitions: 250ms for slide changes
  - Slow transitions: 400ms for major state changes
- Easing: ease-out (feels natural, not mechanical)

**Timing tokens:**
```css
--transition-fast: 150ms ease;
--transition-normal: 250ms ease;
--transition-slow: 400ms ease;
```

**Prohibited:**
- Animated text (individual word/letter animations)
- Spinning/rotating elements
- Bouncing or elastic effects
- Parallax scrolling
- Auto-playing carousels or animations

**Accessibility requirement:**
```css
/* Respect user preference for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Why restricted:** Animations can trigger vestibular disorders and motion sensitivity. They also date quickly (what feels modern now looks tacky in 5 years). Simple cuts and fades are timeless. Always respect the `prefers-reduced-motion` media query.

### Content Guidelines

**Per Slide:**
- One main idea
- 3-5 bullet points maximum
- 40-60 words maximum for body text
- Ample white space (40% minimum)

**Why one idea:** Audiences can absorb one concept at a time. Cramming multiple ideas dilutes impact and overwhelms viewers. If you have two ideas, use two slides.

**Why 3-5 bullets:** More than 5 bullets becomes a wall of text. If you need more, the content should be split across multiple slides or restructured.

**Typography Hierarchy:**
- One h1 per slide (slide title)
- Optional h2 for subsections
- Use font size and weight for emphasis, not color alone (accessibility)

## 8. Do's and Don'ts

### DO:
✓ Use Spirit Purple and Spirit Gold as primary colors  
✓ Maintain minimum 24px font size  
✓ Use Encode Sans Black (900) for headlines  
✓ Leave generous white space (40%+ of slide)  
✓ Test all text for 4.5:1 contrast ratio  
✓ Include alt text for all images  
✓ Use semantic HTML structure  
✓ Keep slides focused (one idea each)  
✓ Use gold bullets for lists  
✓ Place UW logo on title slide  

### DON'T:
✗ Use Spirit Gold as body text (contrast failure)  
✗ Use font sizes below 24px  
✗ Mix multiple accent colors on one slide  
✗ Add gradients, shadows, or heavy effects  
✗ Use decorative fonts or script typefaces  
✗ Crowd slides with excessive content  
✗ Use color as the only indicator (accessibility)  
✗ Forget to test keyboard navigation  
✗ Use more than 5 bullet points per slide  
✗ Skip semantic HTML elements  

## 9. Code Implementation

### CSS Design Tokens

Copy this comprehensive token system into your presentation's header:

```css
:root {
  /* ── PRIMARY BRAND COLORS ────────────────────────────────────────── */
  --uw-husky-purple: #32006e;    /* PMS 2685 — darkest purple */
  --uw-spirit-purple: #4b2e83;   /* PMS 266 — primary digital purple */
  --uw-husky-gold: #b7a57a;      /* Warm gold, print primary */
  --uw-husky-gold-web: #e8e3d3;  /* Light cream gold, digital backgrounds */
  --uw-heritage-gold: #85754d;   /* Deep gold, text on light */
  --uw-spirit-gold: #ffc700;     /* Bright gold, highlights only */
  
  /* ── ACCENT COLORS (≤ 15% of design) ─────────────────────────────── */
  --uw-accent-green: #aadb1e;
  --uw-accent-teal: #2ad2c9;
  --uw-accent-pink: #e93cac;
  --uw-accent-lavender: #c5b4e3;
  
  /* ── NEUTRALS ────────────────────────────────────────────────────── */
  --uw-black: #000000;
  --uw-white: #ffffff;
  --uw-gray-90: #1a1a1a;
  --uw-gray-70: #4d4d4d;
  --uw-gray-50: #808080;
  --uw-gray-30: #b3b3b3;
  --uw-gray-10: #e6e6e6;
  --uw-warm-cream: #e8d3a2;      /* From PPTX theme */
  
  /* ── SEMANTIC COLOR VARIABLES ────────────────────────────────────── */
  /* Backgrounds */
  --bg-primary: var(--uw-spirit-purple);
  --bg-secondary: var(--uw-husky-purple);
  --bg-surface: var(--uw-white);
  --bg-subtle: var(--uw-husky-gold-web);
  --bg-warm: var(--uw-warm-cream);
  
  /* Text */
  --text-primary: var(--uw-husky-purple);
  --text-on-purple: var(--uw-white);
  --text-on-gold: var(--uw-husky-purple);
  --text-body: var(--uw-gray-90);
  --text-muted: var(--uw-gray-70);
  --text-link: var(--uw-spirit-purple);
  --text-link-hover: var(--uw-husky-purple);
  
  /* Borders */
  --border-default: var(--uw-gray-30);
  --border-brand: var(--uw-spirit-purple);
  --border-accent: var(--uw-spirit-gold);
  
  /* Interactive states */
  --focus-ring: var(--uw-spirit-gold);
  --hover-overlay: rgba(75, 46, 131, 0.08);
  --press-overlay: rgba(75, 46, 131, 0.16);
  
  /* ── TYPOGRAPHY TOKENS ───────────────────────────────────────────── */
  /* Font families */
  --font-display: 'Encode Sans', sans-serif;              /* Normal width - default */
  --font-display-wide: 'Encode Sans Wide', sans-serif;    /* Expanded - hero titles */
  --font-display-narrow: 'Encode Sans Narrow', sans-serif;   /* Slightly condensed */
  --font-display-condensed: 'Encode Sans Condensed', sans-serif; /* More condensed */
  --font-display-compressed: 'Encode Sans Compressed', sans-serif; /* Maximum condensed */
  --font-body: 'Open Sans', sans-serif;
  --font-mono: 'Courier New', monospace;
  
  /* Font weights */
  --weight-display: 900;   /* Encode Sans Black */
  --weight-bold: 700;
  --weight-semi: 600;
  --weight-normal: 400;
  --weight-light: 300;
  
  /* Type scale (rem-based for web, px for presentations) */
  --text-3xl: 3rem;        /* 48px — Hero titles */
  --text-2xl: 2.25rem;     /* 36px — Page titles */
  --text-xl: 1.75rem;      /* 28px — Section headers */
  --text-lg: 1.375rem;     /* 22px — Sub-headers */
  --text-md: 1.125rem;     /* 18px — Large body */
  --text-base: 1rem;       /* 16px — Body */
  --text-sm: 0.875rem;     /* 14px — Labels, captions */
  --text-xs: 0.75rem;      /* 12px — Fine print */
  
  /* Line heights */
  --leading-tight: 1.15;
  --leading-snug: 1.35;
  --leading-normal: 1.6;
  --leading-loose: 1.8;
  
  /* Letter spacing */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.05em;
  --tracking-wider: 0.1em;
  --tracking-caps: 0.12em;   /* Used on slide titles */
  
  /* ── SPACING TOKENS (4px base) ───────────────────────────────────── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  
  /* ── BORDER RADIUS ───────────────────────────────────────────────── */
  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 8px;
  --radius-full: 9999px;
  
  /* ── SHADOWS ─────────────────────────────────────────────────────── */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 16px rgba(50,0,110,0.12);
  --shadow-lg: 0 8px 32px rgba(50,0,110,0.18);
  --shadow-brand: 0 4px 20px rgba(75,46,131,0.25);
  
  /* ── TRANSITIONS ─────────────────────────────────────────────────── */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 400ms ease;
}
```

**How to use design tokens:**
```css
section[data-slide="my-slide"] {
  background: var(--uw-spirit-purple);
  padding: var(--space-10);
}

h1 {
  font-family: var(--font-display);
  color: var(--uw-white);
}
```

**Why design tokens:** Design tokens centralize values and make updates easy. If UW changes their purple (unlikely but possible), you update one value, not hundreds.

### Font Loading

**Google Fonts (Recommended):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
```

Note: Encode Sans must be loaded locally (45 font files available in the plugin directory at `~/.claude/plugins/local/uw-slides/fonts/`).

**Local Loading:**
```css
@font-face {
  font-family: 'Encode Sans';
  src: url('../fonts/EncodeSansNormal-900-Black.ttf') format('truetype');
  font-weight: 900;
  font-display: swap;
}

@font-face {
  font-family: 'Encode Sans';
  src: url('../fonts/EncodeSansNormal-800-ExtraBold.ttf') format('truetype');
  font-weight: 800;
  font-display: swap;
}
```

**Why `font-display: swap`:** Shows fallback font immediately while custom font loads. Prevents invisible text during font load (FOIT - flash of invisible text).

### Complete Font Loading Setup

**All Encode Sans variants (local files):**
```css
/* Encode Sans Normal — 9 weights (default, most common) */
@font-face { font-family: 'Encode Sans'; font-weight: 100; src: url('../fonts/EncodeSansNormal-100-Thin.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 200; src: url('../fonts/EncodeSansNormal-200-ExtraLight.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 300; src: url('../fonts/EncodeSansNormal-300-Light.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 400; src: url('../fonts/EncodeSansNormal-400-Regular.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 500; src: url('../fonts/EncodeSansNormal-500-Medium.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 600; src: url('../fonts/EncodeSansNormal-600-SemiBold.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 700; src: url('../fonts/EncodeSansNormal-700-Bold.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 800; src: url('../fonts/EncodeSansNormal-800-ExtraBold.ttf') format('truetype'); font-display: swap; }
@font-face { font-family: 'Encode Sans'; font-weight: 900; src: url('../fonts/EncodeSansNormal-900-Black.ttf') format('truetype'); font-display: swap; }

/* Encode Sans Wide — 9 weights (hero titles) */
@font-face { font-family: 'Encode Sans Wide'; font-weight: 900; src: url('../fonts/EncodeSansWide-900-Black.ttf') format('truetype'); font-display: swap; }
/* ... (repeat for all weights 100-900) */

/* Encode Sans Narrow — 9 weights (long headlines) */
@font-face { font-family: 'Encode Sans Narrow'; font-weight: 900; src: url('../fonts/EncodeSansNarrow-900-Black.ttf') format('truetype'); font-display: swap; }
/* ... (repeat for all weights 100-900) */

/* Encode Sans Condensed — 9 weights (dense data) */
@font-face { font-family: 'Encode Sans Condensed'; font-weight: 900; src: url('../fonts/EncodeSansCondensed-900-Black.ttf') format('truetype'); font-display: swap; }
/* ... (repeat for all weights 100-900) */

/* Encode Sans Compressed — 9 weights (maximum condensation) */
@font-face { font-family: 'Encode Sans Compressed'; font-weight: 900; src: url('../fonts/EncodeSansCompressed-900-Black.ttf') format('truetype'); font-display: swap; }
/* ... (repeat for all weights 100-900) */
```

**Note:** All 45 Encode Sans font files (5 width families × 9 weights) are included in the plugin at `~/.claude/plugins/local/uw-slides/fonts/`. Each width family has all weights from 100 (Thin) to 900 (Black).

## 10. Common Slide Layout Patterns

While the fragment-based architecture gives you complete creative freedom, these proven layout patterns provide starting points for common slide types.

### Pattern 1: Title Slide (Centered)

**Use for:** Opening slide, presentation title

```html
<section data-slide="01-title" aria-label="Title Slide" class="slide">
  <div class="title-container">
    <img src="../assets/W-Logo_Purple_RGB.png" alt="University of Washington W logo" class="uw-logo">
    <h1>Presentation Title</h1>
    <h2>Subtitle or Tagline</h2>
    <div class="presenter-info">
      <p class="name">Presenter Name</p>
      <p class="title">Title or Affiliation</p>
      <p class="date">June 4, 2026</p>
    </div>
  </div>
  
  <style>
    section[data-slide="01-title"] {
      background: var(--uw-spirit-purple);
      color: var(--uw-white);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--space-20);
      position: relative;
    }
    
    section[data-slide="01-title"]::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 8px;
      background: var(--uw-spirit-gold);
    }
    
    section[data-slide="01-title"] .title-container {
      text-align: center;
      max-width: 1200px;
    }
    
    section[data-slide="01-title"] .uw-logo {
      height: 120px;
      filter: brightness(0) invert(1);
      margin-bottom: var(--space-12);
    }
    
    section[data-slide="01-title"] h1 {
      font-family: var(--font-display);
      font-size: 72px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: -0.02em;
      line-height: 1.0;
      margin: 0 0 var(--space-6) 0;
    }
    
    section[data-slide="01-title"] h2 {
      font-family: var(--font-body);
      font-size: 36px;
      font-weight: 400;
      color: var(--uw-husky-gold-web);
      margin: 0 0 var(--space-12) 0;
    }
    
    section[data-slide="01-title"] .presenter-info {
      font-size: 28px;
      line-height: 1.6;
      color: var(--uw-husky-gold-web);
    }
    
    section[data-slide="01-title"] .presenter-info .name {
      font-weight: 600;
      color: var(--uw-white);
      margin-bottom: var(--space-2);
    }
  </style>
</section>
```

### Pattern 2: Standard Content (Light Theme)

**Use for:** Most content slides, bullet lists, text-heavy slides

```html
<section data-slide="02-content" aria-label="Slide 2: Content Title" class="slide">
  <div class="accent-bar-left"></div>
  
  <div class="content-container">
    <h1>Slide Title</h1>
    
    <ul>
      <li>First key point with supporting detail</li>
      <li>Second key point with supporting detail</li>
      <li>Third key point with supporting detail</li>
    </ul>
  </div>
  
  <style>
    section[data-slide="02-content"] {
      background: var(--uw-white);
      color: var(--uw-gray-90);
      padding: var(--space-20);
    }
    
    section[data-slide="02-content"] .content-container {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    section[data-slide="02-content"] h1 {
      font-family: var(--font-display);
      font-size: 56px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: -0.01em;
      color: var(--uw-spirit-purple);
      margin: 0 0 var(--space-12) 0;
    }
    
    section[data-slide="02-content"] ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    section[data-slide="02-content"] li {
      font-size: 32px;
      line-height: 1.6;
      margin-bottom: var(--space-6);
      padding-left: 36px;
      position: relative;
    }
    
    section[data-slide="02-content"] li::before {
      content: '•';
      position: absolute;
      left: 0;
      color: var(--uw-spirit-gold);
      font-weight: 700;
      font-size: 36px;
    }
  </style>
</section>
```

### Pattern 3: Two-Column Layout (Equal Split)

**Use for:** Comparisons, before/after, parallel concepts

```html
<section data-slide="03-comparison" aria-label="Slide 3: Comparison" class="slide">
  <div class="content-container">
    <h1>Before and After</h1>
    
    <div class="columns">
      <div class="column">
        <h2>Before</h2>
        <ul>
          <li>Manual processes</li>
          <li>Time-intensive</li>
          <li>Error-prone</li>
        </ul>
      </div>
      
      <div class="divider"></div>
      
      <div class="column">
        <h2>After</h2>
        <ul>
          <li>Automated workflows</li>
          <li>Efficient</li>
          <li>Validated</li>
        </ul>
      </div>
    </div>
  </div>
  
  <style>
    section[data-slide="03-comparison"] {
      background: var(--uw-white);
      padding: var(--space-20);
    }
    
    section[data-slide="03-comparison"] .content-container {
      max-width: 1600px;
      margin: 0 auto;
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    
    section[data-slide="03-comparison"] h1 {
      font-family: var(--font-display);
      font-size: 56px;
      font-weight: 800;
      color: var(--uw-spirit-purple);
      margin: 0 0 var(--space-12) 0;
    }
    
    section[data-slide="03-comparison"] .columns {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 2px 1fr;
      gap: var(--space-12);
    }
    
    section[data-slide="03-comparison"] .divider {
      background: var(--uw-spirit-gold);
    }
    
    section[data-slide="03-comparison"] h2 {
      font-family: var(--font-display);
      font-size: 36px;
      font-weight: 700;
      color: var(--uw-spirit-purple);
      margin: 0 0 var(--space-8) 0;
    }
    
    section[data-slide="03-comparison"] ul {
      list-style: none;
      padding: 0;
    }
    
    section[data-slide="03-comparison"] li {
      font-size: 28px;
      line-height: 1.6;
      margin-bottom: var(--space-4);
      padding-left: 36px;
      position: relative;
    }
    
    section[data-slide="03-comparison"] li::before {
      content: '•';
      position: absolute;
      left: 0;
      color: var(--uw-spirit-gold);
      font-weight: 700;
      font-size: 32px;
    }
  </style>
</section>
```

### Pattern 4: Transition/Section Slide

**Use for:** Section breaks, chapter dividers

```html
<section data-slide="04-transition" aria-label="Section 2 Transition" class="slide">
  <div class="transition-content">
    <p class="section-number">02</p>
    <h1>Implementation</h1>
    <p class="subtitle">From theory to practice</p>
  </div>
  
  <style>
    section[data-slide="04-transition"] {
      background: var(--uw-spirit-purple);
      color: var(--uw-white);
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    
    section[data-slide="04-transition"]::before,
    section[data-slide="04-transition"]::after {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      height: 8px;
      background: var(--uw-spirit-gold);
    }
    
    section[data-slide="04-transition"]::before { top: 0; }
    section[data-slide="04-transition"]::after { bottom: 0; }
    
    section[data-slide="04-transition"] .transition-content {
      text-align: center;
    }
    
    section[data-slide="04-transition"] .section-number {
      font-family: var(--font-display);
      font-size: 120px;
      font-weight: 900;
      color: var(--uw-spirit-gold);
      opacity: 0.5;
      margin: 0 0 var(--space-4) 0;
      line-height: 1;
    }
    
    section[data-slide="04-transition"] h1 {
      font-family: var(--font-display);
      font-size: 86px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: -0.02em;
      line-height: 1;
      margin: 0 0 var(--space-6) 0;
    }
    
    section[data-slide="04-transition"] .subtitle {
      font-family: var(--font-body);
      font-size: 32px;
      font-weight: 400;
      color: var(--uw-husky-gold-web);
      margin: 0;
    }
  </style>
</section>
```

### Choosing the Right Pattern

| Pattern | Best For | Avoid When |
|---------|----------|------------|
| Title Slide | Opening, credits | Mid-presentation |
| Standard Content | Lists, text, most slides | Heavy visual content |
| Two-Column | Comparisons, parallel concepts | Unrelated content |
| Transition | Section breaks | Frequent use (loses impact) |

**Customization:** These patterns are starting points. Feel free to modify layouts, adjust spacing, change colors within brand guidelines, and create hybrid patterns.

## 11. Pre-Commit Checklist

Before finalizing any slide or presentation, verify compliance with these requirements:

### Brand Compliance
- [ ] Spirit Purple (#4b2e83) used as primary color
- [ ] Spirit Gold (#ffc700) used only for accents (never body text)
- [ ] Accent colors comprise ≤15% of design
- [ ] UW W logo present on title slide
- [ ] Encode Sans Black (900) used for headings
- [ ] Open Sans used for body text

### Accessibility (WCAG 2.1 Level AA)
- [ ] All text meets 4.5:1 contrast ratio minimum
- [ ] Font sizes ≥24px throughout
- [ ] All images have descriptive alt text (or alt="" for decorative)
- [ ] Semantic HTML used (h1, h2, p, ul, section)
- [ ] `aria-label` on each section
- [ ] `lang="en"` on html element
- [ ] Keyboard navigation tested (Tab, Arrow keys, Home, End)
- [ ] Focus indicators visible (2px outline minimum)
- [ ] Color not used as only indicator
- [ ] `prefers-reduced-motion` media query respected

### Content Quality
- [ ] One main idea per slide
- [ ] 3-5 bullet points maximum per slide
- [ ] 40-60 words maximum for body text
- [ ] Ample white space (40%+ of slide)
- [ ] Headings follow hierarchy (h1 → h2, no skipping)
- [ ] Links have meaningful text (not "click here")

### Technical
- [ ] `data-slide` attribute with unique ID
- [ ] `class="slide"` for navigation system
- [ ] All styles scoped with `section[data-slide="..."]` selector
- [ ] CSS variables used for colors and spacing
- [ ] No inline width/height on images (use CSS)
- [ ] File paths correct (relative to build location)

### Testing
- [ ] Slides render correctly in build/index.html
- [ ] Navigation works (arrows, space, click)
- [ ] Slide counter displays correctly
- [ ] No console errors in browser DevTools
- [ ] Run accessibility checker: `/uw-slides:accessibility-check`
- [ ] Test at 1920×1080 resolution
- [ ] Test keyboard-only navigation

## 12. Related Resources

### Official UW Brand Resources
- UW Brand Guidelines: https://www.washington.edu/brand/
- UW Colors: https://www.washington.edu/brand/graphic-elements/primary-color-palette/
- UW Typography: https://www.washington.edu/brand/graphic-elements/font-download/

### Accessibility Resources
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- Color Contrast Checker: https://webaim.org/resources/contrastchecker/
- UW Accessibility: https://www.washington.edu/accessibility/

### Design System Examples
This DESIGN.md format is inspired by Open Design's approach to design systems as readable documentation rather than code libraries. The goal is comprehensive guidance that any LLM or human can read and apply to create brand-compliant designs.

---

## How to Use This Design System

**For LLMs generating slides:**

1. Read this entire document to understand the UW brand
2. When creating a slide, reference the relevant sections:
   - Section 2 for color choices
   - Section 3 for typography
   - Section 4 for layout
   - Section 5 for components
3. Always validate against Section 6 (Accessibility Requirements)
4. Use the code examples in Section 9 as starting points
5. Follow the Do's and Don'ts in Section 8

**For humans:**

This document serves as the complete reference for UW presentation design. You can share it with designers, developers, or anyone creating UW-branded materials. It's intentionally comprehensive and prose-based to be readable without technical background.

**For review:**

Use this document to validate whether a design follows UW brand guidelines. Check each element against the relevant section and verify accessibility requirements.
