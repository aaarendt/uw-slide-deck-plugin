# CloudBank Design System

## Colors

### Primary Brand
```css
--cb-deep-navy:    #1b2c50;   /* Darkest navy — title bars, dark backgrounds */
--cb-signal-blue:  #3a629f;   /* Accent — CTAs, underlines, links */
--cb-ink:          #14161b;   /* Deep contrast — body text, dark strip */
--cb-fog:          #f5f5f5;   /* Alternate section background */
--cb-mist:         #b8c4dc;   /* Light navy tint — subtitles on dark */
```

### Neutrals
```css
--cb-white:    #ffffff;
--cb-black:    #000000;
--cb-gray-90:  #1a1a1a;
--cb-gray-70:  #4d4d4d;
```

## Typography

### Fonts
- **Nunito** (300-900) — Headlines, titles
- **Open Sans** (300-700) — Body text

Both fonts are already loaded by the UW brand CSS via Google Fonts. If this
brand loads standalone, `colors_and_type.css` includes the same @import.

### Type Scale (1920×1080)
- Slide title: 56-86px, Nunito ExtraBold
- Eyebrow: 24-28px, Open Sans SemiBold, uppercase
- Body: 28-34px, Open Sans Regular
- Minimum: 24px (WCAG AA)

## Spacing
Base unit: 8px

```css
--space-3:  24px;
--space-4:  32px;
--space-6:  48px;
--space-8:  64px;
```

## Slide Anatomy

### Dark Slides (Navy)
- Background: deep-navy
- Title: white
- Body: mist (light navy tint)
- Eyebrow: mist — see accessibility note below
- Accent bar: 4px signal-blue (top or left)

### Light Slides (White)
- Background: white or fog
- Title: deep-navy
- Body: ink
- Eyebrow: signal-blue
- Accent bar: 2-4px signal-blue

## Accessibility

**WCAG 2.1 Level AA Required:**
- Contrast: 4.5:1 text, 3:1 large text
- Minimum font size: 24px
- Alt text on all images
- ARIA labels on all sections
- Keyboard navigation

Approved combinations:
✅ Deep-navy on paper:      13.8:1 (AAA)
✅ Ink on paper:            18.1:1 (AAA)
✅ Signal-blue on paper:     6.1:1 (AA)
✅ Paper on deep-navy:      13.8:1 (AAA)
✅ Mist on deep-navy:        7.9:1 (AAA — use for subtitles on dark)
❌ Signal-blue on deep-navy: 2.3:1 (fails all AA — decorative only)

## References
- `colors_and_type.css` — CSS tokens
- `templates/` — Layout templates
