---
name: update-deck
description: Update a deck's managed files (build scripts, shared templates, tools/deckparse.py) to match the current plugin version, without touching slides, content, or assets.
---

# Update Deck

## Purpose

Keep a deck's managed files in sync with the plugin version. `/uw-slides:new-deck` copies build scripts, `shared/header.html`, `shared/footer.html`, and `tools/deckparse.py` into the deck at scaffold time and stamps `.uw-slides.json` with the plugin version. When the plugin is updated, those files drift. This skill shows what has changed and updates them on confirmation.

**Managed files** (the only files this skill may touch):
- `build.sh`
- `build-visuals.sh`
- `outline.sh`
- `publish.sh`
- `shared/footer.html`
- `shared/header.html` (brand-specific)
- `tools/deckparse.py`

**Never touched:** `content/`, `content-with-visuals/`, `slides/`, `assets/`, `deck.yml`, `VISUALS.md`, `OUTLINE.md`, `.brand`, `*.md` files.

## Usage

```
/uw-slides:update-deck
/uw-slides:update-deck --brand=cloudbank
```

Run from inside the presentation directory.

## Procedure

### 1. Read the deck stamp and resolve the plugin

Read `.uw-slides.json`. Take `plugin_version` as the version the deck was scaffolded with.

Find the current plugin directory: check `$UW_SLIDES_HOME` (run `printenv UW_SLIDES_HOME`), otherwise use `~/.claude/plugins/local/uw-slides`. Read `<plugin>/.claude-plugin/plugin.json` to get the current version.

Resolve the brand:
1. `--brand=` flag if provided
2. `.brand` file in the deck directory
3. Default to `uw`

### 2. Diff the managed files

For each managed file, compare the deck's copy with the plugin's canonical copy:

| Deck file | Plugin source |
|-----------|--------------|
| `build.sh` | `<plugin>/templates/build.sh` |
| `build-visuals.sh` | `<plugin>/templates/build-visuals.sh` |
| `outline.sh` | `<plugin>/templates/outline.sh` |
| `publish.sh` | `<plugin>/templates/publish.sh` |
| `shared/footer.html` | `<plugin>/templates/shared/footer.html` |
| `shared/header.html` | `<plugin>/design-systems/<brand>-brand/shared/header.html` |
| `tools/deckparse.py` | `<plugin>/tools/deckparse.py` |

Read both versions and note whether they differ. A file the deck is missing counts as a diff.

### 3. Report and ask for confirmation

Show the user:

```
Deck:   <name>  (scaffolded with uw-slides v<deck-version>)
Plugin: <plugin-path>  (current version: v<current-version>)

Changes found:
  build.sh            — updated
  tools/deckparse.py  — updated
  shared/header.html  — no change
  ...

No changes:
  build-visuals.sh, outline.sh, publish.sh, shared/footer.html
```

If nothing changed, say so and stop.

Ask the user to confirm before writing anything. If they decline, stop.

### 4. Apply the updates

For each changed file the user confirmed:
- Copy the plugin's version over the deck's version.
- Keep the file executable if it was executable before (`build.sh`, `build-visuals.sh`, `outline.sh`, `publish.sh`).

### 5. Update the stamp

Rewrite `.uw-slides.json`, updating `plugin_version` to the current version and `scaffolded_at` to today's date. Preserve `brand` and `catalog`.

### 6. Validate

Run from the deck directory:

```
python3 tools/deckparse.py deck deck.yml
python3 tools/deckparse.py status .
```

If either fails, report the error. The deck's source files (`slides/`, `deck.yml`) have not been touched, so a failure here means the updated script or parser has a compatibility issue — report it and do not mark the update as complete.

## Success output

```
✓ Updated uw-slides: <name>/

  Updated (3):
    build.sh, tools/deckparse.py, shared/footer.html

  Unchanged (4):
    build-visuals.sh, outline.sh, publish.sh, shared/header.html

  .uw-slides.json stamped: v<deck-version> → v<current-version>

Validation passed. Run ./build.sh to rebuild.
```
