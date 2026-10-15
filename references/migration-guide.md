# Migration Guide: SLIDES.md → deck.yml + slides/

Migrate a legacy deck (one that uses `SLIDES.md` for slide ordering) to the current
schema (`deck.yml` + per-slide briefs in `slides/<id>.md`). After migration the deck
builds from `deck.yml` without the deprecation warning, gains per-slide lock/status
tracking and the full layout library, and is ready for `/uw-slides:plan-deck` re-plans.

---

## Prerequisites

- `python3` available on `PATH` (standard library only, no pip)
- The deck has a `SLIDES.md` and a matching set of `content/<id>.html` fragments
- The plugin is at `$UW_SLIDES_HOME` or `~/.claude/plugins/local/uw-slides` (used to
  locate `tools/deckparse.py` if the deck does not already have a vendored copy)
- The deck directory is a git repository (recommended — the migration removes
  `SLIDES.md` from the working tree; it stays in git history)

---

## One-shot migration (recommended)

Open a Claude Code session in your deck directory and run:

```
/uw-slides:extract-to-markdown --migrate
```

This single command:

1. Reads `SLIDES.md` — parses the `## <id>` headings to extract the slide order, and
   the intro block for deck metadata (title, audience, duration).
2. Writes `deck.yml` — title, audience, duration and the ordered `slides:` list.
3. Writes `slides/<id>.md` for each slide — front matter (`id`, `layout: auto`,
   `status: draft`) and body sections (`# Key message`, `## Talking points`,
   `## Notes`) extracted from the matching content under the heading.
4. Writes `.uw-slides.json` (or updates it) — records the plugin version, brand and
   migration date.
5. Validates every output file with `python3 tools/deckparse.py deck deck.yml` and
   `python3 tools/deckparse.py brief slides/<id>.md`; reports and fixes any schema
   errors before finishing.
6. Stages the new files and removes `SLIDES.md` with `git rm` so it remains in git
   history but is no longer in the working tree.
7. Prints a summary table (ID, key message, layout, lines extracted) and next steps.

The skill never overwrites `content/` — existing HTML fragments stay as-is
(`untracked` in `deckparse.py status`) until you regenerate or lock them.

---

## Manual migration

Use this path when you want to inspect or edit the output before removing `SLIDES.md`,
or when you are not in a Claude Code session.

### Step 1 — Extract

```
/uw-slides:extract-to-markdown path/to/index.html
```

This writes `deck.yml` and `slides/<id>.md` briefs from the existing HTML (see the
skill's own documentation for full output details). If you only have `SLIDES.md` and
no HTML, run the migrate flow above, or create the files by hand using the table in
`references/slide-schema.md` section 6 as a mapping guide.

### Step 2 — Review the briefs

Open `deck.yml` and each `slides/<id>.md`. Check:

- `deck.yml` `slides:` order matches the original slide order.
- Each brief has a `# Key message` that matches what is shown large on the slide.
- Bullets under `## Talking points` are talking points, not rendered text.
- Any "note to self" lines from `SLIDES.md` are in `## Notes`, not in talking points.
- `duration` in `deck.yml` is the total in minutes (integer).

### Step 3 — Build and verify

```bash
./build.sh
open build/index.html    # or xdg-open on Linux
```

The build should succeed without a deprecation warning. Compare the result with the
previous `build/index.html` to confirm slides are in the right order.

### Step 4 — Stamp `.uw-slides.json`

If `.uw-slides.json` does not exist yet, create it (or run `/uw-slides:update-deck`
which writes it if missing):

```json
{
  "plugin_version": "0.2.0",
  "brand": "uw",
  "scaffolded_at": "YYYY-MM-DD",
  "catalog": null
}
```

Set `"brand"` to `"uw"` or `"cloudbank"` as appropriate.

### Step 5 — Remove SLIDES.md

```bash
git rm SLIDES.md
git commit -m "chore: migrate to deck.yml + slides/ schema"
```

`SLIDES.md` remains accessible in git history. The build scripts no longer fall back
to it once `deck.yml` is present.

---

## What changes, what stays the same

| | Before (legacy) | After (migrated) |
|---|---|---|
| Slide order | `SLIDES.md` `## <id>` headings | `deck.yml` `slides:` list |
| Per-slide content | Blocks in `SLIDES.md` | `slides/<id>.md` briefs |
| Generated HTML | `content/<id>.html` | Unchanged; re-generate optionally |
| Build command | `./build.sh` | `./build.sh` (same) |
| Deprecation warning | Printed each build | Gone |
| Lock / status tracking | Not available | `locked:`, `status:` in briefs |
| `OUTLINE.md` | Not generated | `./outline.sh` generates it |

---

## After migration: re-generate slides (optional)

If you want to bring slides under the brief-driven workflow — so that changing a brief
marks the corresponding HTML stale and `/uw-slides:generate-slides` can regenerate it
— set `locked: true` in every brief you want to keep as-is, then run:

```
/uw-slides:generate-slides
```

Slides with `locked: true` are skipped. Unlocked slides are regenerated from their
briefs using the layout library.

---

## SLIDES.md deprecation timeline (decision D11)

| Version | Status |
|---------|--------|
| v0.2.0 | `SLIDES.md` fallback deprecated; builds warn and point here |
| v0.3.0 | Fallback removed; `SLIDES.md`-only decks no longer build |

Track removal in the [GitHub issue](https://github.com/aaarendt/uw-slides-plugin/issues) for `SLIDES.md` removal (v0.3.0 milestone).
