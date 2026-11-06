---
name: update-deck
description: Update a deck's managed files (build and publish scripts, shared templates, the CI workflow, vendored tools in tools/) to match the current plugin version, without touching slides, content, or assets.
---

# Update Deck

## Purpose

Keep a deck's managed files in sync with the plugin version. `/uw-slides:new-deck` copies build scripts, `shared/header.html`, `shared/footer.html`, and the tools `tools/deckparse.py`, `tools/lint.py` and `tools/resolve-catalog.py` into the deck at scaffold time and stamps `.uw-slides.json` with the plugin version. When the plugin is updated, those files drift. This skill shows what has changed and updates them on confirmation.

**Managed files** (the only files this skill may touch):
- `build.sh`
- `build-visuals.sh`
- `lint.sh`
- `status.sh`
- `outline.sh`
- `publish.sh`
- `export.sh`
- `.github/workflows/deck.yml`
- `shared/footer.html`
- `shared/header.html` (brand-specific)
- `tools/deckparse.py`
- `tools/lint.py`
- `tools/resolve-catalog.py`

**Never touched:** `content/`, `content-with-visuals/`, `slides/`, `assets/`, `deck.yml` (the deck's metadata and slide order; the CI workflow `.github/workflows/deck.yml` is a different file, and managed), `VISUALS.md`, `OUTLINE.md`, `.brand`, `*.md` files.

**Add-only:** the Claude Code permission rules in `.claude/settings.json` and `.claude/settings.local.json`, and the `.gitignore` line for the local file (step 4b). These are not managed files: the script only adds rules that are missing and keeps everything else in those files.

## Plugin directory

Paths written as `<PLUGIN>/...` are files in the uw-slides plugin, not in the deck. Resolve `PLUGIN` once per invocation. The first match wins, and `<PLUGIN>/tools/deckparse.py` must exist:

1. `$UW_SLIDES_HOME`, if set (`printenv UW_SLIDES_HOME`). Use this to point at a development checkout.
2. The plugin this skill was loaded from, two directories above this `SKILL.md` (`<PLUGIN>/skills/<skill>/SKILL.md`). Take the skill's path from your client, for example Claude Code's "Base directory for this skill", and resolve symlinks. This is where Claude Code, Codex, Copilot and other Agent Plugins clients install the plugin.
3. `~/.claude/plugins/local/uw-slides`, the legacy symlink install.

If none of these has `tools/deckparse.py`, stop and ask the user where the plugin is.

Write every path literally when you run a command. Never use shell variables (`PLUGIN=... python3 $PLUGIN/...`): Claude Code cannot match an allow rule against them, so each run asks for permission.

Run each command exactly as this skill writes it, as one command with nothing appended: no redirects (`2>/dev/null`), no `; echo "exit: $?"`, no `&&`, pipes, loops or leading `cd`. Claude Code checks every part of a compound command, so one part that no rule matches makes the whole command ask. Check whether `UW_SLIDES_HOME` is set by running `printenv UW_SLIDES_HOME` alone (no output means it is not set), and check that a file exists with the Glob or Read tool, not with `ls` or `test` in the shell.

## Usage

```
/uw-slides:update-deck
/uw-slides:update-deck --brand=cloudbank
```

Run from inside the presentation directory.

## Procedure

### 1. Read the deck stamp and resolve the plugin

Read `.uw-slides.json`. Take `plugin_version` as the version the deck was scaffolded with.

Find the current plugin directory as described in Plugin directory above. Read `<PLUGIN>/plugin.json` to get the current version.

Resolve the brand:
1. `--brand=` flag if provided
2. `.brand` file in the deck directory
3. Default to `uw`

### 2. Diff the managed files

First decide which runtime the deck uses, because the shared header and footer come in two versions:

- **reveal.js deck** (every deck scaffolded by the current `/uw-slides:new-deck`): the deck's `shared/footer.html` contains `Reveal.initialize`. Compare against the `-reveal` templates.
- **legacy deck** (scaffolded before reveal.js): it doesn't. Compare against the legacy templates, and never replace a legacy header or footer with a reveal one, or a reveal one with a legacy one: the two need different markup and assets, so swapping one alone breaks the deck.

For each managed file, compare the deck's copy with the plugin's canonical copy:

| Deck file | Plugin source |
|-----------|--------------|
| `build.sh` | `<PLUGIN>/templates/build.sh` |
| `build-visuals.sh` | `<PLUGIN>/templates/build-visuals.sh` |
| `lint.sh` | `<PLUGIN>/templates/lint.sh` |
| `status.sh` | `<PLUGIN>/templates/status.sh` |
| `outline.sh` | `<PLUGIN>/templates/outline.sh` |
| `publish.sh` | `<PLUGIN>/templates/publish.sh` |
| `export.sh` | `<PLUGIN>/templates/export.sh` |
| `.github/workflows/deck.yml` | `<PLUGIN>/templates/.github/workflows/deck.yml` |
| `shared/footer.html` | reveal.js deck: `<PLUGIN>/templates/shared/footer-reveal.html`; legacy deck: `<PLUGIN>/templates/shared/footer.html` |
| `shared/header.html` | reveal.js deck: `<PLUGIN>/design-systems/<brand>-brand/shared/header-reveal.html`; legacy deck: `<PLUGIN>/design-systems/<brand>-brand/shared/header.html` |
| `tools/deckparse.py` | `<PLUGIN>/tools/deckparse.py` |
| `tools/lint.py` | `<PLUGIN>/tools/lint.py` |
| `tools/resolve-catalog.py` | `<PLUGIN>/tools/resolve-catalog.py` |

Read both versions and note whether they differ. A file the deck is missing counts as a diff: decks scaffolded by older plugin versions may have no `tools/lint.py`, `tools/resolve-catalog.py` or `.github/workflows/deck.yml`, and this adds them.

`export.sh` and `.github/workflows/deck.yml` became managed in v0.6.0, and users may have edited their copies (the old `export.sh` told them to). When one of these differs, show the user the diff and point out any of their own changes that the update would remove, so they can decide.

### 3. Report and ask for confirmation

Show the user:

```
Deck:   <name>  (scaffolded with uw-slides v<deck-version>)
Plugin: <plugin-path>  (current version: v<current-version>)
Runtime: reveal.js   (or: legacy)

Changes found:
  build.sh            — updated
  tools/deckparse.py  — updated
  shared/header.html  — no change
  ...
Permissions: 12 Claude Code allow rules missing (.claude/settings.json, .claude/settings.local.json)

No changes:
  build-visuals.sh, outline.sh, publish.sh, shared/footer.html
```

Also check the Claude Code permission rules, which keep the other skills from asking about every command (the rules are not a managed file: the deck's own settings are never overwritten, only missing rules are added). Run from the deck directory, with `<PLUGIN>` written as the resolved absolute path:

```
python3 <PLUGIN>/tools/deckperms.py . --check
```

It prints the rules it would add to `.claude/settings.json` (shared with the deck's repository) and `.claude/settings.local.json` (this computer only), or says there is nothing to add. Add a `Permissions:` line to the report below for it. The recommended user-level allow rule for this command, so it does not ask in every deck, is `Bash(python3 */tools/deckperms.py *)` (the `*` stands for the version-numbered plugin folder).

If no managed file changed and no permission rule is missing, say so and stop.

Ask the user to confirm before writing anything. If they decline, stop.

### 4. Apply the updates

For each changed file the user confirmed:
- Copy the plugin's version over the deck's version.
- Keep the file executable if it was executable before (`build.sh`, `build-visuals.sh`, `outline.sh`, `publish.sh`, `export.sh`); a `*.sh` file this adds is made executable.

### 4b. Add the permission rules

If the check in step 3 found missing rules and the user confirmed, run from the deck directory:

```
python3 <PLUGIN>/tools/deckperms.py .
```

It merges the missing rules into `.claude/settings.json` and `.claude/settings.local.json` and adds the local file to `.gitignore`. It keeps everything already in those files and exits 1 without changing a file that is not valid JSON; report that error and carry on. Tell the user `.claude/settings.json` is meant to be committed with the deck, so the rules reach anyone who clones it.

### 5. Update the stamp

Rewrite `.uw-slides.json`, updating `plugin_version` to the current version and `scaffolded_at` to today's date, and setting `plugin_dir` to `<PLUGIN>` as the resolved absolute path (add the field if the deck has none). Preserve `brand` and `catalog`. Decks whose `plugin_dir` is stale after a plugin update are fixed by this step.

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

  .uw-slides.json stamped: v<deck-version> → v<current-version> (plugin_dir updated)
  Permissions: added 11 rules to .claude/settings.json and 1 to .claude/settings.local.json (or: already up to date)

Validation passed. Run ./build.sh to rebuild.
```
