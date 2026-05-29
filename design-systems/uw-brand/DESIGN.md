# University of Washington Design System

## Colors

### Primary Brand
```css
--uw-husky-purple:   #32006e;
--uw-spirit-purple:  #4b2e83;
--uw-husky-gold-web: #e8e3d3;
--uw-heritage-gold:  #85754d;
--uw-spirit-gold:    #ffc700;
```

### Neutrals
```css
--uw-white:    #ffffff;
--uw-black:    #000000;
--uw-gray-90:  #1a1a1a;
--uw-gray-70:  #4d4d4d;
```

## Typography

### Fonts
- **Encode Sans** (100-900) — Headlines, titles
- **Open Sans** (300-700) — Body text

### Type Scale (1920×1080)
- Slide title: 56-86px, Encode Sans Black
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

### Dark Slides (Purple)
- Background: spirit-purple or husky-purple
- Title: white
- Body: husky-gold-web (cream)
- Eyebrow: spirit-gold
- Accent bar: 8px gold (top or left)

### Light Slides (White)
- Background: white
- Title: spirit-purple
- Body: gray-90 or black
- Accent bar: 8px gold

## Accessibility

**WCAG 2.1 Level AA Required:**
- Contrast: 4.5:1 text, 3:1 large text
- Minimum font size: 24px
- Alt text on all images
- ARIA labels on all sections
- Keyboard navigation

Approved combinations:
✅ White on spirit-purple: 12.6:1
✅ Heritage-gold on white: 4.9:1
❌ Spirit-gold on white: 1.9:1 (fails)

## References
- `colors_and_type.css` — CSS tokens
- `deck-stage.js` — Slide engine
- `templates/` — Layout templates
