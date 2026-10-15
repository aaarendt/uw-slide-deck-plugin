# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Versions follow semantic versioning: MAJOR.MINOR.PATCH. Deprecations are noted under the version they are introduced in; scheduled removals name the target version.

---

## [Unreleased]

---

## [0.2.0] — in progress

This release completes the restructuring started in v0.1.x (WS0–WS5). Breaking changes are limited to the deprecated `SLIDES.md` fallback.

### Added
- **WS1 — Versioning and path independence**
  - New decks scaffold `tools/deckparse.py` (vendored copy) so all skill commands run as `python3 tools/deckparse.py ...` with no variable expansion. Recommended allow rule: `Bash(python3 tools/deckparse.py *)`.
  - New decks write `.uw-slides.json` (plugin version, brand, scaffold date) to the deck root.
  - New `/uw-slides:update-deck` skill: diffs and updates managed files (build scripts, shared templates, `tools/deckparse.py`) against the current plugin; never touches `content/`, `slides/`, or `assets/`.
  - `UW_SLIDES_HOME` is the canonical way to point to a non-default plugin location; `~/.claude/plugins/local/uw-slides` remains the documented default fallback.
- **WS2 — Schemas** (`references/slide-schema.md`, `tools/deckparse.py`, `templates/deck.yml`, `templates/slides/_example.md`)
- **WS3 — Layout library** (12 layouts in `templates/layouts/*.html`, `references/layouts.md`)
- **WS4 — plan-deck skill** (`skills/plan-deck/SKILL.md`)
- **WS5 — Generation and deck.yml build** (`skills/generate-slides/SKILL.md`, updated build scripts, `outline.sh`, `OUTLINE.md` generation)
- **WS6 — Slide catalog and resolver** (`catalog/catalog.yml`, 6 seeded slides, `tools/resolve-catalog.py`, `catalog/CURATION.md`)
- **WS7 — Lint and CI** (`tools/lint.py`, `templates/lint.sh`, `templates/status.sh`, `templates/.github/workflows/deck.yml`)
- **WS9 — Collaboration process**
  - `CONTRIBUTING.md`: prerequisites, clone-to-preview guide, roles (brief vs HTML), branch/PR workflow, how to lock a slide, regenerating on a branch, model/prompt context in commits, license and attribution notes for Encode Sans (SIL OFL), Open Sans (Apache 2.0), UW brand assets, and deck images.
  - `.github/CODEOWNERS` and `.github/pull_request_template.md` for the plugin repo.
  - `templates/.github/CODEOWNERS` (pattern for slide ownership) and `templates/.github/pull_request_template.md` scaffolded into new decks by `new-deck`.

### Deprecated
- **`SLIDES.md`** as a slide-ordering source. Decks that only have `SLIDES.md` still build but print a deprecation warning pointing to the migration guide (`references/slide-schema.md`, section 6). Scheduled removal: v0.3.0.

### Changed
- All skill `deckparse.py` calls now use `tools/deckparse.py` (deck-relative) rather than `$UW_SLIDES_HOME/tools/deckparse.py` (variable expansion).
- `templates/AGENTS.md`: explains plugin path resolution via `UW_SLIDES_HOME` / default fallback instead of hard-coding `~/.claude/plugins/local/uw-slides`.
- `design-systems/uw-brand/DESIGN.md`: font path references updated to reflect plugin-relative locations.

---

## [0.1.0] — 2025

Initial release (WS0 baseline fixes).

### Added
- Fragment-based slide architecture (`content/<id>.html`, scoped `section[data-slide="..."]` CSS).
- Two-pass workflow: content (pass 1) → visuals (pass 2) → publish (pass 3).
- UW and CloudBank design systems.
- Skills: `new-deck`, `generate-slides`, `apply-visuals`, `design-review`, `accessibility-check`, `extract-to-markdown`.
- Build scripts: `build.sh`, `build-visuals.sh`, `publish.sh`, `outline.sh`.
- `tools/deckparse.py`: stdlib-only YAML parser for `deck.yml` and slide briefs.
- `deck.yml` + `slides/<id>.md` brief architecture (replaces `SLIDES.md` for new decks).

---

## Release and tagging process

1. Update the version in `.claude-plugin/plugin.json`.
2. Move `[Unreleased]` entries under a new `[x.y.z] — YYYY-MM-DD` heading.
3. Commit: `chore(release): bump to vX.Y.Z`.
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
5. Push tag: `git push origin vX.Y.Z`.
