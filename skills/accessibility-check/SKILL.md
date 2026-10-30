---
name: accessibility-check
description: Validate WCAG 2.1 Level AA compliance. Checks contrast ratios, font sizes, alt text, ARIA labels, and semantic HTML.
---

# Accessibility Check Skill

## Purpose
Validate WCAG 2.1 Level AA compliance for slide decks.

## Plugin directory

Paths written as `<PLUGIN>/...` are files in the uw-slides plugin, not in the deck. Resolve `PLUGIN` once per invocation. The first match wins, and `<PLUGIN>/tools/deckparse.py` must exist:

1. `$UW_SLIDES_HOME`, if set (`printenv UW_SLIDES_HOME`). Use this to point at a development checkout.
2. The plugin this skill was loaded from, two directories above this `SKILL.md` (`<PLUGIN>/skills/<skill>/SKILL.md`). Take the skill's path from your client, for example Claude Code's "Base directory for this skill", and resolve symlinks. This is where Claude Code, Codex, Copilot and other Agent Plugins clients install the plugin.
3. `~/.claude/plugins/local/uw-slides`, the legacy symlink install.

If none of these has `tools/deckparse.py`, stop and ask the user where the plugin is.

## What Gets Checked

**Deterministic checks (run `./lint.sh` first — these are already covered):**
- Alt text on all `<img>` elements (`lint.py` checks `img-missing-alt`)
- `aria-label` on every `<section>` (`lint.py` checks `missing-aria-label`)
- Font-size floor of 1.5rem for body text, 1rem absolute minimum (`lint.py` checks `font-size-too-small` / `font-size-below-minimum`)

**Judgment checks (unique to this skill — run after lint passes):**
1. **Color Contrast** — 4.5:1 for normal text, 3:1 for large text; verify token pairings in the slides match approved brand combinations
2. **Semantic HTML** — Proper heading hierarchy (`<h1>` for key message, `<h2>`/`<h3>` for sub-sections); no skipped heading levels
3. **Keyboard Navigation** — Arrow keys navigate slides (via `shared/footer.html`); no keyboard traps
4. **Focus Management** — Visible focus indicator present; interactive elements reachable
5. **Reading Order** — DOM order matches visual order for screen readers

## Slides

Check the fragments in `content/` (or `content-with-visuals/` when checking pass 2), numbered by their position in `deck.yml` (legacy decks: `SLIDES.md` headings). Fix problems in the brief or by regenerating (`/uw-slides:generate-slides`), not by hand-editing a generated slide, unless its brief has `locked: true`.

## Brand Resolution

Resolve the brand in this order:
1. `--brand=` flag if provided
2. `.brand` file in the current directory if it exists
3. Default to `uw`

## Usage
```bash
/uw-slides:accessibility-check
/uw-slides:accessibility-check --brand=cloudbank
```

The optional `--brand=<uw|cloudbank>` parameter overrides auto-detection and selects which brand's approved contrast pairings to reference when reporting results. If omitted, the brand is read from `.brand` in the deck directory (written by `new-deck` at scaffold time). The WCAG 2.1 AA thresholds (4.5:1 text, 3:1 large text) apply to both brands. For approved CloudBank contrast combinations, see `<PLUGIN>/design-systems/cloudbank-brand/DESIGN.md`.

## Output
```
✅ PASSED (18 checks)
❌ FAILED (2 checks)
  - Slide 05: Missing alt text for 'diagram.png'
  - Slide 12: Contrast 3.2:1 (needs 4.5:1)
```

See `<PLUGIN>/references/accessibility-requirements.md` for complete guidelines.
