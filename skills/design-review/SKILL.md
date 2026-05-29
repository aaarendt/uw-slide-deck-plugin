---
name: design-review
description: Validate UW brand compliance. Checks color tokens, fonts, layout patterns, logo usage, and design system adherence.
---

# Design Review Skill

## Purpose
Ensure slide deck follows UW brand guidelines.

## What Gets Checked
1. **Color Tokens** — Use CSS variables, not hardcoded hex
2. **Font Usage** — Only approved UW fonts
3. **Layout Patterns** — Use approved templates
4. **Logo Treatment** — Correct inversion on dark backgrounds
5. **Accent Bar** — 8px gold bar on every slide
6. **Type Scale** — Follow UW hierarchy

## Usage
```bash
claude code /uw-slides:design-review
```

## Output
```
✅ Brand Compliant
❌ Violations:
  - Slide 03: Hardcoded color #4b2e83 (use var(--uw-spirit-purple))
  - Slide 08: Missing accent bar
```

See `references/brand-guidelines.md` for complete requirements.
