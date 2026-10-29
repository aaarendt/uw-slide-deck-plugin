---
name: design-review
description: Validate UW brand compliance. Checks color tokens, fonts, layout patterns, logo usage, and design system adherence.
---

# Design Review Skill

## Purpose
Ensure slide deck follows UW brand guidelines.

## Plugin directory

Paths written as `<PLUGIN>/...` are files in the uw-slides plugin, not in the deck. Resolve `PLUGIN` once per invocation. The first match wins, and `<PLUGIN>/tools/deckparse.py` must exist:

1. `$UW_SLIDES_HOME`, if set (`printenv UW_SLIDES_HOME`). Use this to point at a development checkout.
2. The plugin this skill was loaded from, two directories above this `SKILL.md` (`<PLUGIN>/skills/<skill>/SKILL.md`). Take the skill's path from your client, for example Claude Code's "Base directory for this skill", and resolve symlinks. This is where Claude Code, Codex, Copilot and other Agent Plugins clients install the plugin.
3. `~/.claude/plugins/local/uw-slides`, the legacy symlink install.

If none of these has `tools/deckparse.py`, stop and ask the user where the plugin is.

## What Gets Checked

**Deterministic checks (run `./lint.sh` first — these are already covered):**
- Font-size floor: `clamp()` minimum below 1.5rem for body text, or below 1rem for any text (`lint.py` checks `font-size-below-minimum` / `font-size-too-small`)
- CSS selector scoping to `section[data-slide="..."]` (`lint.py` checks `css-not-scoped`)
- `<img>` alt text (`lint.py` checks `img-missing-alt`)
- `aria-label` on `<section>` (`lint.py` checks `missing-aria-label`)

**Judgment checks (unique to this skill — run after lint passes):**
1. **Color Tokens** — CSS variables used consistently; no hardcoded hex for brand colors
2. **Font Usage** — Only approved fonts for the brand; no system-font fallbacks used as primary
3. **Layout Patterns** — `data-layout` is a layout-library ID or `custom`; layout matches slide purpose
4. **Logo Treatment** — Correct inversion on dark backgrounds
5. **Accent Bar** — Every slide has a brand accent bar:
   - `--brand=uw`: 8px `--uw-spirit-gold` bar
   - `--brand=cloudbank`: 4px `--cb-signal-blue` bar
6. **Type Scale** — Brand hierarchy respected; display font used for headlines
7. **CloudBank contrast rule** *(brand=cloudbank only)* — Any text element whose computed foreground is `--cb-signal-blue` and whose background is `--cb-deep-navy` or `--bg-primary` → **FAIL** with: "Signal Blue on Deep Navy fails WCAG AA (2.25:1). Use `--cb-mist` (7.86:1) for subtitles on dark, or `--cb-white` (13.79:1) for titles."

## Slides

Review the fragments in `content/` (or `content-with-visuals/` when reviewing pass 2), numbered by their position in `deck.yml` (legacy decks: `SLIDES.md` headings). Fix violations in the brief or by regenerating (`/uw-slides:generate-slides`), not by hand-editing a generated slide, unless its brief has `locked: true`.

## Brand Resolution

Resolve the brand in this order:
1. `--brand=` flag if provided
2. `.brand` file in the current directory if it exists
3. Default to `uw`

## Usage
```bash
/uw-slides:design-review
/uw-slides:design-review --brand=cloudbank
```

The optional `--brand=<uw|cloudbank>` parameter overrides auto-detection. If omitted, the brand is read from `.brand` in the deck directory (written by `new-deck` at scaffold time).

## Output
```
✅ Brand Compliant
❌ Violations:
  - Slide 03: Hardcoded color #4b2e83 (use var(--uw-spirit-purple))
  - Slide 08: Missing accent bar
  - Slide 11 [cloudbank]: Signal Blue on Deep Navy fails WCAG AA (2.25:1). Use --cb-mist for subtitles on dark, or --cb-white for titles.
```

See `<PLUGIN>/design-systems/<brand>-brand/DESIGN.md` for complete brand requirements.
