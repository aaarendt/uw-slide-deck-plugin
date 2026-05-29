---
name: accessibility-check
description: Validate WCAG 2.1 Level AA compliance. Checks contrast ratios, font sizes, alt text, ARIA labels, and semantic HTML.
---

# Accessibility Check Skill

## Purpose
Validate WCAG 2.1 Level AA compliance for UW slide decks.

## What Gets Checked
1. **Color Contrast** — 4.5:1 for text, 3:1 for large text
2. **Font Sizes** — Minimum 24px
3. **Alt Text** — All images must have descriptions
4. **ARIA Labels** — All slides have aria-label
5. **Semantic HTML** — Proper heading hierarchy
6. **Keyboard Navigation** — Arrow keys functional

## Usage
```bash
claude code /uw-slides:accessibility-check
```

## Output
```
✅ PASSED (18 checks)
❌ FAILED (2 checks)
  - Slide 05: Missing alt text for 'diagram.png'
  - Slide 12: Contrast 3.2:1 (needs 4.5:1)
```

See `references/accessibility-requirements.md` for complete guidelines.
