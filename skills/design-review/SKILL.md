---
name: design-review
description: Validate UW brand compliance. Checks color tokens, fonts, layout patterns, logo usage, and design system adherence.
---

# Design Review Skill

## Purpose
Ensure slide deck follows UW brand guidelines.

## What Gets Checked
1. **Color Tokens** — Use CSS variables, not hardcoded hex
2. **Font Usage** — Only approved fonts for the brand
3. **Font Size Floor** — All visible text must use `clamp()` with a minimum of `1.5rem` (24pt). Exception: source/citation lines and decorative uppercase labels may use `1rem` minimum. Hard-coded values below `1.5rem` for content text are a violation. Presentations are projected — small text is unreadable past the third row of an audience.
4. **Layout Patterns** — Use approved templates
5. **Logo Treatment** — Correct inversion on dark backgrounds
6. **Accent Bar** — Every slide must have a brand accent bar:
   - `--brand=uw`: 8px `--uw-spirit-gold` bar
   - `--brand=cloudbank`: 4px `--cb-signal-blue` bar
7. **Type Scale** — Follow brand hierarchy
8. **CloudBank contrast rule** *(brand=cloudbank only)* — Any text element whose computed foreground is `--cb-signal-blue` and whose background is `--cb-deep-navy` or `--bg-primary` → **FAIL** with: "Signal Blue on Deep Navy fails WCAG AA (2.25:1). Use `--cb-mist` (7.86:1) for subtitles on dark, or `--cb-white` (13.79:1) for titles."

## Usage
```bash
claude code /uw-slides:design-review
claude code /uw-slides:design-review --brand=cloudbank
```

The optional `--brand=<uw|cloudbank>` parameter selects which brand rules to apply. Defaults to `uw`.

## Output
```
✅ Brand Compliant
❌ Violations:
  - Slide 03: Hardcoded color #4b2e83 (use var(--uw-spirit-purple))
  - Slide 08: Missing accent bar
  - Slide 11 [cloudbank]: Signal Blue on Deep Navy fails WCAG AA (2.25:1). Use --cb-mist for subtitles on dark, or --cb-white for titles.
```

See `design-systems/<brand>-brand/DESIGN.md` for complete brand requirements.
