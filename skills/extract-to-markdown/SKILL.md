---
name: extract-to-markdown
description: Extract slide content from an existing HTML presentation into deck.yml and slides/<id>.md briefs (or, for legacy use, a SLIDES.md outline); also migrates legacy SLIDES.md decks to the current schema
---

# Extract to Markdown Skill

## Purpose
Turn an existing HTML slide deck into the planning files of a fragment-based deck: `deck.yml` (order and metadata) and one brief per slide in `slides/<id>.md` (format: `references/slide-schema.md`). Use it to import a deck made elsewhere, or to rebuild briefs for a deck that only has HTML.

Also provides a **one-shot migration** (`--migrate`) for legacy decks that use `SLIDES.md` as their slide source, converting them to `deck.yml` + briefs without touching `content/`.

## Usage
```bash
/uw-slides:extract-to-markdown path/to/index.html                    # deck.yml + slides/*.md (default)
/uw-slides:extract-to-markdown --migrate [deck-dir]                  # migrate SLIDES.md → deck.yml + slides/*.md
/uw-slides:extract-to-markdown path/to/index.html --format=slides-md # legacy SLIDES.md outline (deprecated)
```
All `deckparse.py` commands use the vendored copy at `tools/deckparse.py` (put there by `/uw-slides:new-deck`). The recommended allow rule is `Bash(python3 tools/deckparse.py *)`.

## What It Does (HTML → briefs)
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
4. Validates everything: `python3 tools/deckparse.py deck deck.yml` and `... brief slides/<id>.md` for each brief; fixes any error it reports before finishing.
5. Reports image references per slide (not written to the briefs: visuals belong in `VISUALS.md`, pass 2).

## Rules (HTML → briefs)
- **Never overwrite existing files.** If `deck.yml` or any `slides/<id>.md` already exists, stop and ask whether to skip, rename or replace.
- Do not touch `content/`. Existing HTML stays as it is (`untracked` in `deckparse.py status`) until `/uw-slides:generate-slides` regenerates it. To keep an imported slide exactly as it is, set `locked: true` in its brief.
- Only the fields in `references/slide-schema.md` are valid. No `## Visual notes` or `## Speaker notes` headings: use `## Notes`.

---

## Migrate flow (`--migrate`)

Converts a legacy deck in place: reads `SLIDES.md`, writes `deck.yml` + `slides/<id>.md` briefs, stamps `.uw-slides.json`, then removes `SLIDES.md`.

**Full procedure:**

See `references/migration-guide.md` for a step-by-step guide with verification steps.

### Inputs

| | |
|---|---|
| Deck directory | Current directory or the path passed as the second argument |
| `SLIDES.md` | Must exist; must not already have `deck.yml` (stop and ask if it does) |

### Steps

1. Parse `SLIDES.md`:
   - Extract deck title and intro metadata (audience, duration) from the first block before the first `## ` heading.
   - Collect each `## <id>` heading (valid ID: `^[a-z0-9]+(-[a-z0-9]+)*$`); skip headings that do not look like slide IDs (e.g. `## How to render this deck`).
   - For each heading, collect the lines until the next heading: identify key message (first non-blank line or explicit "Key message:" label), talking points (bulleted lines), notes ("Note to self:" block or similar), and source ("Source:" line).

2. Write `deck.yml`:
   ```yaml
   title: <extracted title or "Untitled">
   audience: <extracted or omit if absent>
   duration: <integer minutes or omit>
   slides:
     - <id-1>
     - <id-2>
     ...
   ```

3. Write `slides/<id>.md` for each slide (front matter + body per `references/slide-schema.md`):
   ```markdown
   ---
   id: <id>
   layout: auto
   status: draft
   ---

   # Key message
   <key message text>

   ## Talking points
   - <point>

   ## Notes
   <notes if any>
   ```

4. Write or update `.uw-slides.json` (do not overwrite `brand` if already set):
   ```json
   {
     "plugin_version": "0.2.0",
     "brand": "uw",
     "scaffolded_at": "<YYYY-MM-DD>",
     "catalog": null
   }
   ```

5. Validate all output:
   - `python3 tools/deckparse.py deck deck.yml`
   - `python3 tools/deckparse.py brief slides/<id>.md` for each brief
   - Fix any reported errors before continuing.

6. Build check: run `./build.sh` and confirm it exits 0 with no deprecation warning (the deprecation warning triggers only when `deck.yml` is absent — with `deck.yml` present, it must not appear).

7. Remove `SLIDES.md`:
   - If the deck directory is a git repository: `git rm SLIDES.md` (keeps it in history).
   - Otherwise: move to `SLIDES.md.bak` and tell the user to delete it once they are satisfied.

8. Print a summary:
   ```
   ✓ Migrated 12 slides
     deck.yml, slides/01-title.md ... slides/12-closing.md
     .uw-slides.json updated
     SLIDES.md removed (kept in git history)

   Next: review briefs, run ./build.sh, then /uw-slides:generate-slides to regenerate any slide.
   ```

### Rules (migrate)

- **Never overwrite `deck.yml` or any `slides/<id>.md`** if they already exist. If `deck.yml` is present, stop and report: "This deck already has deck.yml. Run /uw-slides:plan-deck to re-plan, or delete deck.yml and slides/ to re-migrate."
- Never touch `content/`. Existing HTML is preserved; it is `untracked` until regenerated.
- Keep all content; when intent is ambiguous (is a line a talking point or a note?), default to `## Talking points` and add a VERIFY comment in `## Notes`.
- IDs must match the existing `content/<id>.html` filenames — derive IDs from the `## ` headings, not from the HTML.
- Validate before removing `SLIDES.md`; never remove it if validation failed.

---

## Legacy output (`--format=slides-md`)
Writes `SLIDES.md` in the current directory, as before (deprecated, see `references/slide-schema.md` section 6 for migration):

```markdown
# Extracted Presentation

## 01-title
Title: Original Title
Content: Extracted text...
```

## Output report (HTML → briefs)
```
✓ Extracted 12 slides
  deck.yml, slides/01-title.md ... slides/12-closing.md
  Layouts recognised: 4 (rest: auto)
  Images: 03-architecture (diagram.png), 07-team (team.jpg)
```

Next: edit the briefs, then run `/uw-slides:generate-slides`.
