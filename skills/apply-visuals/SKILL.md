---
name: apply-visuals
description: Apply pass-2 visual additions from VISUALS.md to existing slide HTML fragments
---

# Apply Visuals (Pass 2)

## Purpose

Read `VISUALS.md` and add the specified visual elements — photographs, diagrammatic accents, icons — to the already-rendered HTML slide fragments from pass 1. Write modified fragments to `content-with-visuals/`. Do not touch `content/`.

## Brand Resolution

Resolve the brand in this order:
1. `--brand=` flag if provided
2. `.brand` file in the current directory if it exists
3. Default to `uw`

## Usage

```
/uw-slides:apply-visuals
/uw-slides:apply-visuals --brand=cloudbank
```

Run from inside the presentation directory, or with the presentation directory as context. Pass 1 must be done first — `content/` must contain the rendered slide fragments (`/uw-slides:generate-slides`, then `./build.sh`). All `deckparse.py` commands use the vendored copy at `tools/deckparse.py` (put there by `/uw-slides:new-deck`). The recommended allow rule is `Bash(python3 tools/deckparse.py *)`.

## Behavior

**Start fresh on every invocation.** `VISUALS.md`, `deck.yml` and the files in `content/` and `content-with-visuals/` change between runs: the user adds entries, edits wording and regenerates slides. Re-read them from disk every time this skill runs, even if you read them earlier in the same conversation, and never work from memory of a previous run. Do steps 1-3 before looking at any idempotency marker.

1. Read `VISUALS.md` in full: the global styling rules and **every** `## <slide-id>` entry under `# Per-slide additions`. Write down the complete list of entry IDs; this list, not what was applied last time, defines the work.
2. Get the authoritative slide list and ordering from `deck.yml` (`python3 tools/deckparse.py deck deck.yml --format ids`). Legacy decks without `deck.yml` use the `## slide-id` headings of `SLIDES.md` (deprecated).
3. Run `python3 tools/deckparse.py status .`. If a slide you are about to modify is `missing` or `stale`, tell the user to run `/uw-slides:generate-slides` first: visuals added to out-of-date pass-1 HTML would be out of date too. `locked` slides are fine (you only read `content/`).
4. For each slide listed in `VISUALS.md` under `## Per-slide additions` (all of them, including entries added since the last run):
   - If the entry says "No additions" — skip. Do not copy the file.
   - Otherwise — read `content/<slide-id>.html`, apply the specified additions, write the result to `content-with-visuals/<slide-id>.html`. Only now apply the idempotency check below, per slide: it may skip that one slide, never the whole run.
5. Slides in `deck.yml` that are not mentioned under `## Per-slide additions` in `VISUALS.md` — skip. They will be served from `content/` by `build-visuals.sh`.
6. **Reconcile before reporting.** Every entry ID from step 1 must appear in your report with a disposition: applied, skipped (no additions), skipped (already applied), out of date, conflict, or skipped with a reason (for example an ID that is not in `deck.yml`). If any entry has no disposition, you skipped it by mistake: go back and handle it.
7. Run `./build-visuals.sh` to produce `build/index-with-visuals.html`.

To place a visual in free space, read the slide's brief (`slides/<id>.md`) and its `data-layout`: `references/layouts.md` describes each layout's regions (for example `bullets` leaves the right side open). The brief's talking points and notes are never rendered, so a visual must not restate them.

## Idempotency

This check is made **per slide, after** the work list from `VISUALS.md` has been built (Behavior steps 1-4). A slide that is already applied does not mean the others are: a re-run exists precisely to pick up entries added since last time. Before writing to `content-with-visuals/<slide-id>.html`, check whether the file already exists and already contains a `data-visuals-applied` marker on the root `<section>` element. If it does, skip that slide and report "already applied" — do not add the visual elements a second time.

When writing a modified fragment, add `data-visuals-applied="true"` to the root `<section>` element so subsequent runs can detect it.

**Preserve provenance.** Keep `data-slide`, `data-layout`, `data-brief-hash` and `data-generated-by` on the root `<section>` exactly as they are in `content/<slide-id>.html`. The copy in `content-with-visuals/` keeps the hash of the brief it was derived from.

**Out-of-date copies.** If an existing `content-with-visuals/<slide-id>.html` has a `data-brief-hash` that differs from `python3 tools/deckparse.py hash slides/<slide-id>.md` (or from `content/<slide-id>.html`), the slide's text changed after pass 2 ran. Report "pass-2 copy is out of date", and re-apply from the current `content/` file only after the user confirms.

## How to apply visual elements

### Diagrammatic accents (SVG)

Create inline SVG elements using the global styling rules from `VISUALS.md`:
- Thin uniform stroke, no filled shapes
- Accent color: `uw` → `var(--uw-spirit-gold)`; `cloudbank` → `var(--cb-signal-blue)`
- Geometric and minimal — two or three strokes per mark
- Small scale — the slide's typography remains primary
- Scope styles inside `section[data-slide="..."] svg { ... }` to avoid leaking

Place the SVG at the location described in the per-slide entry (above a callout, beside a phrase, between columns, etc.). If no placement is specified, default to the slide's visually open area without obscuring text.

### Photographs

**Image paths.** The deck is viewed from `build/index.html`, so every `src` is relative to `build/`: write `../assets/images/<filename>`, never `assets/images/<filename>` (that resolves to `build/assets/...` and shows a broken image; `publish.sh` would also warn "not found"). When `VISUALS.md` names only a file (`team-photo.jpg`), it lives in `assets/images/`; use `../assets/images/team-photo.jpg`. Use `../assets/diagrams/<filename>` for diagram image files. If the entry gives a path (for example `assets/images/team/photo.jpg`), keep its folders and prefix `../`. Do not touch `http(s)` URLs.

If the named file exists in `assets/images/`, insert:
```html
<img src="../assets/images/<filename>" alt="[description from VISUALS.md]" class="slide-photo">
```
Add a scoped `.slide-photo` style to position and size the image as described. If a caption is specified, add a `<figcaption>` wrapped in a `<figure>`.

If no file is named, or the named file is not in `assets/images/` yet, insert a commented placeholder (and list it in the report so the user knows to add the file):
```html
<!-- PHOTO PLACEHOLDER: [description from VISUALS.md] -->
<!-- Replace src with ../assets/images/<filename> when the file is available -->
<img src="" alt="[description]" class="slide-photo" style="display:none">
```

### Conflict handling

If a visual element would require moving or resizing first-pass content to fit, the first-pass layout wins. Flag the conflict in a comment in the HTML:
```html
<!-- VISUAL CONFLICT: [element] not applied — would override first-pass layout. Review manually. -->
```
Report the conflict to the user after completing the pass.

## File locations

All paths are relative to the presentation directory:

| File | Role |
|------|------|
| `deck.yml` | Authoritative slide list and ordering (legacy decks: `SLIDES.md`) |
| `slides/<id>.md` | Slide briefs (read-only in pass 2) |
| `VISUALS.md` | Pass-2 additions specification |
| `content/<id>.html` | Pass-1 source fragments (read-only in pass 2) |
| `content-with-visuals/<id>.html` | Pass-2 output fragments |
| `build/index-with-visuals.html` | Final assembled deck with visuals |

## VISUALS.md format

`VISUALS.md` uses `#`-level headings for global sections and `##`-level headings for per-slide entries, matching slide IDs in `deck.yml`:

```markdown
# Per-slide additions

## 01-title
No additions.

## 03-some-slide
**Diagrammatic addition.** Description of what to add and where...

**Photographic addition.** Description of the photo and placement...
```

Slide identifiers in `VISUALS.md` must match the IDs in `deck.yml` exactly. If a `VISUALS.md` entry references a slide ID that doesn't exist in `content/`, report the mismatch and skip.

## Success output

After completing the pass, report:

```
✓ Pass 2 complete

Applied visuals:
  03-some-slide — diagrammatic accent + photo placeholder
  05-another-slide — diagrammatic accent

Skipped (no additions):
  01-title, 02-opening, 10-another

Skipped (already applied):
  (none)

Conflicts:
  (none)

Run ./build-visuals.sh to assemble the final deck.
```
