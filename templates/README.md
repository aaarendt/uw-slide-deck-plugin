# [Presentation Name]

[BRAND_NAME] presentation using a two-pass, fragment-based architecture.

## Pass 1 — Content and structure

1. Edit `deck.yml` (title, audience, objectives, slide order) and one brief per slide in `slides/<id>.md`
2. Run `/uw-slides:generate-slides` (reads the briefs, writes `content/`)
3. Build: `./build.sh`
4. Preview: `open build/index.html`
5. Rehearse and revise the briefs, regenerate and rebuild — repeat until content is settled
6. Optional: `./outline.sh` writes `OUTLINE.md`, a generated read-only overview (never edit it)

## Pass 2 — Visual additions

1. Edit `VISUALS.md` to specify photographs, diagrammatic accents, and icons
2. Run `/uw-slides:apply-visuals` (LLM reads VISUALS.md, writes to `content-with-visuals/`)
3. Build: `./build-visuals.sh`
4. Preview: `open build/index-with-visuals.html`

## Pass 3 — Publish (portable file)

1. Run: `./publish.sh` (requires `python3`)
2. Share: `build/index-published.html` — fully self-contained, all images inlined as base64

## Reordering Slides

Move a line in the `slides:` list of `deck.yml`, then rebuild with `./build.sh`.

A slide ID is lowercase letters, digits and single hyphens, such as `03-approach`. Each ID needs a brief `slides/<id>.md` and a fragment `content/<id>.html`. Format: `references/slide-schema.md` in the plugin.

To edit a generated slide by hand, first set `locked: true` in its brief; otherwise the next `generate-slides` run replaces your edit. Regeneration asks before overwriting a slide whose brief changed.

## Build options

- `./build.sh --strict` fails if a slide listed in `deck.yml` has no fragment (default: warn and skip)
- `./build.sh /path/to/deck` builds a deck from another directory
- Both options also apply to `./build-visuals.sh`

## Structure

- `deck.yml` — Deck metadata, objectives and slide order
- `slides/` — One brief per slide (message, layout, notes, owner, status)
- `OUTLINE.md` — Generated overview of the deck (created by `./outline.sh`)
- `VISUALS.md` — Pass-2 visual additions specification
- `content/` — Pass-1 HTML fragments generated from the briefs (never modified by pass 2)
- `content-with-visuals/` — Pass-2 HTML fragments (only slides that received additions)
- `shared/` — Header and footer templates
- `build/` — Generated presentations (git-ignored)
- `assets/` — Images and diagrams
