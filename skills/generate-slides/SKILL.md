---
name: generate-slides
description: Generate content/<id>.html slide fragments from slides/<id>.md briefs using the layout library. Skips locked and catalog slides, reports stale slides and asks before overwriting.
---

# Generate Slides (Pass 1)

## Purpose

Turn the briefs in `slides/<id>.md` (ordered by `deck.yml`) into HTML fragments in `content/<id>.html`. The brief is the source of truth; the HTML is a regenerable artifact that records which version of the brief it came from.

This skill replaces the old "read SLIDES.md and write slides by conversation" step. Legacy decks that only have `SLIDES.md` are not handled here: migrate them first (mapping in `references/slide-schema.md`, section 6), or keep writing fragments by hand.

## Brand Resolution

Resolve the brand in this order:
1. `--brand=` flag if provided
2. `.brand` file in the current directory if it exists
3. Default to `uw`

## Usage

```
/uw-slides:generate-slides                 # generate missing slides, ask about stale ones
/uw-slides:generate-slides <id> [<id>...]  # only these slides
```

Run from inside the presentation directory. In the commands below, `$PLUGIN` is `$UW_SLIDES_HOME` if set, otherwise `~/.claude/plugins/local/uw-slides`.

## Read first

- `design-systems/<brand>-brand/DESIGN.md`: the brand rules
- `references/layouts.md`: the layout library, slot limits, fill procedure (section 2) and `custom` rules (section 6)
- `references/slide-schema.md`: brief fields, staleness hash, generation rules (section 5)
- `references/accessibility-requirements.md`
- the font-size rules in the plugin `CLAUDE.md` (minimum `1.5rem`; `1rem` only for source lines and uppercase labels)

## Procedure

### 1. Get the state of every slide

```bash
python3 "$PLUGIN/tools/deckparse.py" status .
```

It prints one line per slide in `deck.yml` order. Act on the state, never on guesses:

| State | Meaning | Action |
|-------|---------|--------|
| `missing` | no `content/<id>.html` | generate |
| `stale` | the brief changed since the HTML was generated | list these, **ask before overwriting**, then generate the confirmed ones |
| `untracked` | HTML exists without `data-brief-hash` (hand-written or older) | **ask**: overwrite, or keep it by setting `locked: true` in the brief |
| `fresh` | HTML matches the brief | skip |
| `locked` | brief has `locked: true` (hand-edited HTML) | **never write**; report it. To regenerate, the user sets `locked: false` |
| `catalog` | brief has `use: catalog/<id>` | skip; catalog slides are copied by the catalog resolver, never generated |
| `no-brief`, `invalid` | `slides/<id>.md` missing or does not parse | skip and report the file and line; the user fixes it |

If the user named slide IDs, restrict to those. If `deck.yml` itself does not parse, stop and show the error. `orphan-brief` and `orphan-fragment` lines are reported, not acted on.

### 2. Generate each slide

For every slide you are going to write:

1. **Read the brief**: `python3 "$PLUGIN/tools/deckparse.py" brief slides/<id>.md` (JSON: front matter and body).
2. **Resolve the layout.**
   - A layout ID: it must be a file in `templates/layouts/` (`layouts.md`, section 1). Unknown ID: stop and report.
   - `auto`: choose with `layouts.md`, section 5, **write the chosen ID and a `layout_rationale` back into the brief's front matter**, and only then continue (the hash covers `layout`).
   - `custom`: follow `layout_intent` and the rules in `layouts.md`, section 6.
3. **Check the content fits** the layout's limits (`layouts.md`, section 4). If it does not, report it and propose either shorter text (for the user to approve in the brief) or a different layout. Never shrink fonts or silently cut the brief's text.
4. **Fill the layout** exactly as in `layouts.md`, section 2: copy `templates/layouts/<layout>.html`, rename `layout-<layout>` to the slide ID in `data-slide` and every CSS selector, fill each `data-slot` / `data-param`, remove optional elements the brief leaves empty. `custom` slides are written from scratch to the same standard (scoped `section[data-slide="<id>"]` styles, brand tokens, one `<h1>`, accent bar).
5. **Apply the generation rules** (`slide-schema.md`, section 5):
   - the key message is the headline and usually the main text shown;
   - talking points and notes are **never** rendered;
   - the source renders as the small footer line;
   - pass 1 uses no photographs and no decorative icons: it must look finished without images;
   - `aria-label` is `Slide N: <title, else key message>`, where N is the position in `deck.yml`.
6. **Stamp provenance** on the root `<section>`, after any write-back to the brief:
   - `data-layout="<layout id or custom>"`
   - `data-brief-hash="<output of python3 "$PLUGIN/tools/deckparse.py" hash slides/<id>.md>"`
   - `data-generated-by="uw-slides@<plugin version>"` (version from `$PLUGIN/.claude-plugin/plugin.json`)
7. **Write** `content/<id>.html` (create `content/` if needed).

### 3. Build and report

```bash
./build.sh
./outline.sh        # refreshes OUTLINE.md (read-only overview)
```

Then run `/uw-slides:design-review` and `/uw-slides:accessibility-check`, and report:

```
✓ Generated:   02-why-cloud (bullets), 05-demo (exercise)
↻ Regenerated: 03-costs (stale, confirmed)
⏭ Fresh:       01-title
🔒 Locked:      04-diagram (hand-edited; not touched)
📦 Catalog:     06-intro (catalog resolver)
⚠ Skipped:     07-recap (slides/07-recap.md:12: unknown field 'colour')
Layout choices written back to briefs: 02-why-cloud (auto -> bullets)
```

## Rules

- **Never overwrite a locked slide, and never overwrite a stale or untracked one without asking.** If the user wants to hand-edit generated HTML, tell them to set `locked: true` in the brief first, or the next run will replace the edit.
- Changing `layout_rationale`, `objective`, `owner`, `status`, `duration`, `locked`, `section` or `## Notes` does not make a slide stale; changing the key message, talking points, source, slots, `title`, `layout`, `layout_intent`, `use` or `params` does.
- Fix problems in the brief or the layout choice, not by hand-tuning one slide's CSS away from the library.
- Slide fragments only ever touch `content/`. Pass 2 (`apply-visuals`) writes `content-with-visuals/`.
