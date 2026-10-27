# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Versions follow semantic versioning: MAJOR.MINOR.PATCH. Deprecations are noted under the version they are introduced in; scheduled removals name the target version.

---

## [Unreleased]

### Added
- Catalog slides `cb-what-is`, `cb-programs`, `cb-why-choose`, `cb-award-tiers` and `cb-process` (CloudBank brand, verbatim, `status: review`): the standard CloudBank introduction (what it is, services, reasons to choose it, award tiers, application process). On-slide text is condensed; the full wording is in the speaker notes. Each `slide.md` lists its source pages and the facts that still need the owner's check, notably the award-tier figures.
- Catalog slide `cb-eligibility` (CloudBank brand, verbatim, `status: review`): who can lead a CloudBank project and recommended uses. Full source wording is kept in the speaker notes.

### Changed
- `catalog/CURATION.md` now admits program slides (standard slides for a program such as CloudBank) alongside framing slides, with a brand and ID prefix per program, a size guideline per program, and rules for policy wording that changes.
- `plan-deck` checks a program's catalog slides against planned content slides in decks of that program's brand, not only framing roles.
- Catalog `agenda` 1.1.0 groups slides into parts: slides that share a `section:` become one item (or, without sections, each `section-divider` and the slides after it), with their minutes summed. New optional `slide.md` field `in_agenda: false` keeps framing catalog slides out of the agenda; the six seeded framing slides set it.
- Catalog slides without a `title` now take their `aria-label`, and their agenda label, from their own heading instead of the catalog description.

### Fixed
- Slide text was centered on every slide in reveal.js decks, because `reveal.css` centers slide text and neither brand header overrode it. Both `header-reveal.html` files now set `text-align: left` on `section.slide`. Layouts meant to be centered (`title`, `closing`, `stat-callout` and the centered catalog slides) set it themselves and are unchanged. Existing decks pick this up with `/uw-slides:update-deck`.
- The `agenda` catalog slide ran off the bottom of the screen in decks with more than about 9 content slides. It now uses two balanced columns past 7 items and caps the list at 12, which fits at 1280×720 even when labels wrap; past 12 the resolver shows 11 plus "and N more" and warns.
- The `agenda` listed framing catalog slides by their IDs ("title", "land-ack", "funding", "feedback"), ignored `section: hidden`, and used two color tokens no brand defines, so its heading was plain black. All fixed.

---

## [0.2.0] — 2026-10-15

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
- **WS8 — Runtime and export**
  - Adopted reveal.js 6.0.2 (MIT, ~169 KB) as the presentation runtime. Replaces the homegrown `footer.html` navigation for new decks.
  - `design-systems/uw-brand/shared/header-reveal.html` and `design-systems/cloudbank-brand/shared/header-reveal.html`: reveal-compatible headers (`.reveal > .slides` wrapper; `display: flex` slide system; speaker-notes hide rule).
  - `templates/shared/footer-reveal.html`: initialises reveal.js with `width: '100%', height: '100%'` to preserve `vw`-based font sizes.
  - `templates/setup-reveal.sh`: downloads `reveal.min.js` + `reveal.min.css` from jsDelivr into `assets/reveal/`.
  - `templates/export.sh`: Playwright-based PDF export (optional dependency).
  - `skills/generate-slides/SKILL.md`: `## Notes` brief sections now render as `<aside class="notes">` for reveal.js presenter view.
  - `skills/new-deck/SKILL.md`: new decks use reveal variants and run `setup-reveal.sh` at scaffold time.
  - `docs/runtime-evaluation.md`: decision record, compatibility analysis, migration guide, vw/font-size note.
- **WS9 — Collaboration process**
  - `CONTRIBUTING.md`: prerequisites, clone-to-preview guide, roles (brief vs HTML), branch/PR workflow, how to lock a slide, regenerating on a branch, model/prompt context in commits, license and attribution notes for Encode Sans (SIL OFL), Open Sans (Apache 2.0), UW brand assets, and deck images.
  - `.github/CODEOWNERS` and `.github/pull_request_template.md` for the plugin repo.
  - `templates/.github/CODEOWNERS` (pattern for slide ownership) and `templates/.github/pull_request_template.md` scaffolded into new decks by `new-deck`.
- **WS11 — Migration and documentation**
  - `references/migration-guide.md`: step-by-step guide for migrating a legacy `SLIDES.md` deck to `deck.yml` + `slides/<id>.md` briefs. Covers the one-shot skill path and manual migration.
  - `/uw-slides:extract-to-markdown --migrate`: new migrate-deck flow — reads `SLIDES.md`, writes `deck.yml` + briefs + `.uw-slides.json`, validates with `deckparse.py`, then removes `SLIDES.md` (keeps it in git history). Full rules in the updated `skills/extract-to-markdown/SKILL.md`.
  - `templates/VISUALS.md`: "How to use this file" preamble replaced with a one-line pointer to `skills/apply-visuals/SKILL.md`, which is the stated authority for pass-2 rules. Deck-specific content (global styling sections, per-slide entries) is unchanged.
  - `references/migration-guide.md` added to `references/` index in `CLAUDE.md`.
  - `.claude-plugin/plugin.json`: `skills` array added listing all eight skill names; `keywords` updated to include `catalog`, `reveal-js` and `migration`.
  - `README.md`: "Migrating from SLIDES.md" section added; Skills table updated to include `update-deck`.

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
