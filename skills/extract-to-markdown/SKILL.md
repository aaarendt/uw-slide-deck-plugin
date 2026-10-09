---
name: extract-to-markdown
description: Extract slide content from an existing HTML presentation into deck.yml and slides/<id>.md briefs (or, for legacy use, a SLIDES.md outline)
---

# Extract to Markdown Skill

## Purpose
Turn an existing HTML slide deck into the planning files of a fragment-based deck: `deck.yml` (order and metadata) and one brief per slide in `slides/<id>.md` (format: `references/slide-schema.md`). Use it to import a deck made elsewhere, or to rebuild briefs for a deck that only has HTML.

## Usage
```bash
/uw-slides:extract-to-markdown path/to/index.html                    # deck.yml + slides/*.md (default)
/uw-slides:extract-to-markdown path/to/index.html --format=slides-md # legacy SLIDES.md outline (deprecated)
```
In the commands below, `$PLUGIN` is `$UW_SLIDES_HOME` if set, otherwise `~/.claude/plugins/local/uw-slides`.

## What It Does
1. Parses the HTML deck into slides (each `<section>`, or the deck's own slide element).
2. For each slide, writes a brief:
   - `id`: the `data-slide` value if it is a valid ID (lowercase letters, digits, single hyphens), otherwise `NN-<slug of the heading>`; IDs are unique
   - `# Key message`: the slide's main heading or headline
   - `layout`: the slide's `data-layout` when it is a layout-library ID (`references/layouts.md`), otherwise `auto`
   - `## Talking points`: other visible text and bullets, as a starting point (the user decides what is spoken and what is shown)
   - `## Source`: citation or source lines
   - `## Notes`: speaker notes or "note to self" text, if present
   - `status: draft`
3. Writes `deck.yml` with `title` (the document title or first heading) and `slides:` in the original order.
4. Validates everything: `python3 "$PLUGIN/tools/deckparse.py" deck deck.yml` and `... brief slides/<id>.md` for each brief; fixes any error it reports before finishing.
5. Reports image references per slide (not written to the briefs: visuals belong in `VISUALS.md`, pass 2).

## Rules
- **Never overwrite existing files.** If `deck.yml` or any `slides/<id>.md` already exists, stop and ask whether to skip, rename or replace.
- Do not touch `content/`. Existing HTML stays as it is (`untracked` in `deckparse.py status`) until `/uw-slides:generate-slides` regenerates it. To keep an imported slide exactly as it is, set `locked: true` in its brief.
- Only the fields in `references/slide-schema.md` are valid. No `## Visual notes` or `## Speaker notes` headings: use `## Notes`.

## Legacy output (`--format=slides-md`)
Writes `SLIDES.md` in the current directory, as before (deprecated, see `references/slide-schema.md` section 6 for migration):

```markdown
# Extracted Presentation

## 01-title
Title: Original Title
Content: Extracted text...
```

## Output report
```
✓ Extracted 12 slides
  deck.yml, slides/01-title.md ... slides/12-closing.md
  Layouts recognised: 4 (rest: auto)
  Images: 03-architecture (diagram.png), 07-team (team.jpg)
```

Next: edit the briefs, then run `/uw-slides:generate-slides`.
