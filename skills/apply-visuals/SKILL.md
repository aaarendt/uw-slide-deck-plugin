---
name: apply-visuals
description: Apply pass-2 visual additions from VISUALS.md to existing slide HTML fragments
---

# Apply Visuals (Pass 2)

## Purpose

Read `VISUALS.md` and add the specified visual elements — photographs, diagrammatic accents, icons — to the already-rendered HTML slide fragments from pass 1. Write modified fragments to `content-with-visuals/`. Do not touch `content/`.

## Usage

```
/uw-slides:apply-visuals
```

Run from inside the presentation directory, or with the presentation directory as context. Pass 1 (`build.sh`) must have been run first — `content/` must exist and contain the rendered slide fragments.

## Behavior

1. Read `VISUALS.md` to understand global styling rules and per-slide additions.
2. Read `SLIDES.md` to get the authoritative slide list and ordering.
3. For each slide listed in `VISUALS.md` under `## Per-slide additions`:
   - If the entry says "No additions" — skip. Do not copy the file.
   - Otherwise — read `content/<slide-id>.html`, apply the specified additions, write the result to `content-with-visuals/<slide-id>.html`.
4. Slides in `SLIDES.md` that are not mentioned under `## Per-slide additions` in `VISUALS.md` — skip. They will be served from `content/` by `build-visuals.sh`.
5. Run `./build-visuals.sh` to produce `build/index-with-visuals.html`.

## Idempotency

Before writing to `content-with-visuals/<slide-id>.html`, check whether the file already exists and already contains a `data-visuals-applied` marker on the root `<section>` element. If it does, skip that slide and report "already applied" — do not add the visual elements a second time.

When writing a modified fragment, add `data-visuals-applied="true"` to the root `<section>` element so subsequent runs can detect it.

## How to apply visual elements

### Diagrammatic accents (SVG)

Create inline SVG elements using the global styling rules from `VISUALS.md`:
- Thin uniform stroke, no filled shapes
- Gold color: use `var(--uw-spirit-gold)` or `var(--uw-husky-gold-web)`
- Geometric and minimal — two or three strokes per mark
- Small scale — the slide's typography remains primary
- Scope styles inside `section[data-slide="..."] svg { ... }` to avoid leaking

Place the SVG at the location described in the per-slide entry (above a callout, beside a phrase, between columns, etc.). If no placement is specified, default to the slide's visually open area without obscuring text.

### Photographs

Insert an `<img>` tag with the following defaults if no specific file is named:
```html
<img src="assets/images/[placeholder]" alt="[description from VISUALS.md]" class="slide-photo">
```
Add a scoped `.slide-photo` style to position and size the image as described. If a caption is specified, add a `<figcaption>` wrapped in a `<figure>`.

If the specific photo file is not yet available, insert a commented placeholder:
```html
<!-- PHOTO PLACEHOLDER: [description from VISUALS.md] -->
<!-- Replace src with actual file path when available -->
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
| `SLIDES.md` | Authoritative slide list and ordering |
| `VISUALS.md` | Pass-2 additions specification |
| `content/<id>.html` | Pass-1 source fragments (read-only in pass 2) |
| `content-with-visuals/<id>.html` | Pass-2 output fragments |
| `build/index-with-visuals.html` | Final assembled deck with visuals |

## VISUALS.md format

`VISUALS.md` uses `#`-level headings for global sections and `##`-level headings for per-slide entries, matching the `##` convention in `SLIDES.md`:

```markdown
# Per-slide additions

## 01-title
No additions.

## 03-some-slide
**Diagrammatic addition.** Description of what to add and where...

**Photographic addition.** Description of the photo and placement...
```

Slide identifiers in `VISUALS.md` must match `SLIDES.md` exactly. If a `VISUALS.md` entry references a slide ID that doesn't exist in `content/`, report the mismatch and skip.

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
