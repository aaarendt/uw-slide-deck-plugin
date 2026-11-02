# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Versions follow semantic versioning: MAJOR.MINOR.PATCH. Deprecations are noted under the version they are introduced in; scheduled removals name the target version.

---

## [Unreleased]

### Added
- Catalog slide `cb-title` (CloudBank brand, parameterized): the CloudBank title slide, with the same params as `uw-title` (`title`, `subtitle`, `presenter`, `affiliation` defaulting to "CloudBank", `date`). A CloudBank deck can now be assembled entirely from catalog slides, starting with a title (#42).
- `tools/new-deck.py` scaffolds a deck in one command: `python3 <PLUGIN>/tools/new-deck.py <name> [--brand=uw|cloudbank]`. It does everything `/uw-slides:new-deck` used to do with about twenty separate commands (templates, brand header and footer, fonts for `uw`, the vendored tools, `.github/` files, `.brand`, `.uw-slides.json`, `deck.yml` and the starter briefs), validates the result and runs `setup-reveal.sh`. A failed reveal.js download is a warning, not a failure. It refuses to touch an existing folder, rejects names that are not safe as a folder name, removes the folder it created if a step fails, and makes every `*.sh` executable (`setup-reveal.sh` and `export.sh` were not executable in the plugin). Tests: `tools/test_new_deck.py`, including a check that its managed-files list matches `/uw-slides:update-deck`.

### Changed
- `/uw-slides:new-deck` runs that script instead of copying files one by one, so Claude Code asks for permission once instead of about twenty times, and the result is the same every run, in seconds and with few tokens. The README documents the allow rule `Bash(python3 */tools/new-deck.py *)`; the `*` stands in for the version-numbered plugin folder (#50).
- Every skill's "Plugin directory" section now says to write paths literally and never use shell variables (`PLUGIN=... $PLUGIN/...`), which Claude Code cannot match against an allow rule (#50).

## [0.3.1] — 2026-11-02

Catalog slides no longer need a separate step: `/uw-slides:generate-slides` resolves them, and the deck's resolver finds the catalog of a marketplace install on its own. In existing decks, run `/uw-slides:update-deck` once to get the updated resolver and record where the plugin is installed.

### Changed
- The deck's `tools/resolve-catalog.py` can find the catalog of a marketplace install without `--catalog`: `/uw-slides:new-deck` and `/uw-slides:update-deck` record the plugin location as `plugin_dir` in `.uw-slides.json`, and the resolver reads it after `$UW_SLIDES_HOME`. A missing or stale path is ignored, and the "Catalog not found" message then points to `/uw-slides:update-deck`. The resolver's docstring now documents that a vendored copy also looks in `<deck>/catalog` (#34).
- `/uw-slides:generate-slides` now resolves catalog slides itself: before generating layout slides it runs `tools/resolve-catalog.py resolve . --catalog=<PLUGIN>/catalog` and reports the resolver's output, including placeholder and brand warnings, with its own. Users no longer need the `--catalog` path (#39, most of #34). `/uw-slides:plan-deck`'s next steps, the README walkthrough (step 4, "Using a catalog slide", troubleshooting) and `catalog/README.md` shrink to a single `/uw-slides:generate-slides`.

## [0.3.0] — 2026-11-02

This release makes the plugin installable from a marketplace in Claude Code, Codex and GitHub Copilot CLI, simplifies the slide catalog and fixes `/uw-slides:update-deck`. Breaking changes: the Claude Code marketplace is renamed from `uw-slides-local` to `uw-slide-deck` (README, "Upgrading from the symlink install"), and the catalog's `land-ack` slide is removed (catalog 2.0.0). Run `/uw-slides:update-deck` in existing decks to pick up the new scripts and tools. The `SLIDES.md` fallback, planned for removal in this release, stays deprecated; its removal moves to a later release (#22).

### Added
- The plugin is now an [Agent Plugins v1.0.0](https://agent-plugins.org/specification) package, installable in Claude Code, Codex and GitHub Copilot CLI, with linked-skill instructions for OpenCode (README, Installation). New root `plugin.json` (portable manifest) next to `.claude-plugin/plugin.json`, and a Codex marketplace in `.agents/plugins/marketplace.json`.
- `tools/validate_plugin.py` checks the manifest rules, that both manifests match, skill front matter, that every skill using `<PLUGIN>/` paths says how to find the plugin, and both marketplaces. `--claude` also runs `claude plugin validate`. Tests: `tools/test_validate_plugin.py`.
- Catalog slides `cb-what-is`, `cb-programs`, `cb-why-choose`, `cb-award-tiers` and `cb-process` (CloudBank brand, verbatim): the standard CloudBank introduction (what it is, services, reasons to choose it, award tiers, application process). On-slide text is condensed; the full wording is in the speaker notes. Each `slide.md` lists its source pages.
- Catalog slide `cb-eligibility` (CloudBank brand, verbatim): who can lead a CloudBank project and recommended uses. Full source wording is kept in the speaker notes.

- The catalog resolver warns when a resolved slide still shows `PLACEHOLDER` wording, such as the `funding` slide's default agency, grant ID and grant title, and names the values left to set.

### Changed
- Skills find the plugin through `$UW_SLIDES_HOME`, then the plugin they were loaded from (two directories above their `SKILL.md`), then `~/.claude/plugins/local/uw-slides`. Before, an install anywhere but that path needed `UW_SLIDES_HOME`. Every skill now names plugin files as `<PLUGIN>/...`, so they're not confused with files in the deck. The deck `AGENTS.md` template gives other agents the same order.
- Skills pass `--catalog=<PLUGIN>/catalog` to the deck's vendored `resolve-catalog.py`. The resolver also looks for a `catalog/` next to its own `tools/` directory. The `resolve` and `eject` commands in `catalog/README.md`, `catalog/CURATION.md` and the catalog slides' `slide.md` files pass the flag too, because a deck's copy of the resolver can't find the catalog of a marketplace install on its own.
- Skills read the plugin version from `plugin.json` instead of `.claude-plugin/plugin.json`.
- The Claude Code marketplace is renamed from `uw-slides-local` to `uw-slide-deck`, and the homepage and repository URLs now point at `aaarendt/uw-slide-deck-plugin` (the old `uw-slides-plugin` URL returns 404).
- `catalog/CURATION.md` now admits program slides (standard slides for a program such as CloudBank) alongside framing slides, with a brand and ID prefix per program, a size guideline per program, and rules for policy wording that changes.
- `plan-deck` checks a program's catalog slides against planned content slides in decks of that program's brand, not only framing roles.
- Catalog `agenda` 1.1.0 groups slides into parts: slides that share a `section:` become one item (or, without sections, each `section-divider` and the slides after it), with their minutes summed. New optional `slide.md` field `in_agenda: false` keeps framing catalog slides out of the agenda; the six seeded framing slides set it.
- Catalog slides without a `title` now take their `aria-label`, and their agenda label, from their own heading instead of the catalog description.
- `/uw-slides:update-deck` now also keeps `tools/resolve-catalog.py` in sync, and adds it (and `tools/lint.py`) to decks scaffolded before they were vendored (#33). When a deck has no vendored `deckparse.py` or `lint.py`, the deck scripts now suggest running `/uw-slides:update-deck` instead of only setting `UW_SLIDES_HOME`.
- README reorganised for new users: a plain description and a screenshot of a built slide at the top, install for Claude Code first with other agents after, a step-by-step "Make your first deck" written around what each skill does (generate-slides already builds and runs both checks; apply-visuals builds pass 2), with two ways to fill a deck: plan it with plan-deck, or assemble it from catalog slides without planning, which uses few or no tokens. Covers revising, visuals and publishing, and lists the deck scripts separately for running without an agent (replaces Quick Start and the two-pass workflow), "What's in your deck folder", and two new troubleshooting entries. Maintainer material (packaging, how skills find the plugin, changing defaults, adding a brand) moved to "For plugin developers" at the end. The README no longer tells you to run `./setup-reveal.sh` after scaffolding (new-deck already runs it), and its "change the defaults" list names the `-reveal` header and footer that new decks actually use.
- README: new "Catalog Slides" section (what the catalog holds, what `ready`/`draft`/`review` mean, how to use, resolve and eject a catalog slide), and the resolve step added to Quick Start and the two-pass workflow. New "Switching from the symlink install" and "Working on the plugin" sections replace "Local checkout (development)" (#35); CONTRIBUTING's test step now uses `claude --plugin-dir`. The "Migrating from SLIDES.md" section is removed; `references/migration-guide.md` and `/uw-slides:extract-to-markdown --migrate` are unchanged.
- `tools/validate_plugin.py` also checks the Codex marketplace entry's required `policy` and `category`, and that both marketplaces use the same category. The Claude Code marketplace category changes from `development` to `productivity` to match Codex (#36).

- Catalog slides no longer have a `status` field (`draft` / `review` / `ready`): a slide in the catalog is ready to use, and slides whose wording isn't approved stay out of it. plan-deck now uses any catalog slide whose description fits, so the CloudBank introduction slides (accepted by their owner on 2026-11-02) are picked for CloudBank decks; before, as `review` slides, they never were. Their "Status note" sections became "Sources". A `PLACEHOLDER` value the planner can't fill becomes a `VERIFY:` line. Slide briefs in a deck keep their own `status:` (`draft` / `review` / `done`), which is unrelated.
- The catalog version is now 2.0.0, because a slide was removed (see Removed).

- The `SLIDES.md` deprecation warning in `build.sh` and `build-visuals.sh` no longer names v0.3.0 as the removal release; removal moves to a later release (#22).
### Removed
- Catalog slide `land-ack`. Its text was a placeholder and there is no approved wording to replace it; `catalog/CURATION.md` says how to add one once there is. A deck that used it fails to resolve that slide ("catalog slide metadata not found"); its existing `content/<id>.html` is kept, so to keep the slide, replace `use: catalog/land-ack` in its brief with `locked: true` and add a `# Key message` line (as eject would have), or remove the slide from `deck.yml`.

### Fixed
- `/uw-slides:update-deck` compared a deck's `shared/header.html` and `shared/footer.html` with the legacy (non-reveal.js) templates, although new-deck scaffolds them from `header-reveal.html` and `footer-reveal.html`. On current decks it reported both as changed and, if confirmed, replaced them with versions that don't start reveal.js; fixes to the reveal headers never reached existing decks. It now detects the deck's runtime and compares against the matching templates.
- `catalog/README.md` said `/uw-slides:generate-slides` resolves catalog slides. It skips them; the resolver runs separately.
- `tools/validate_plugin.py` crashed when a marketplace's `plugins` was not an array, read folded (`>`) and literal (`|`) skill descriptions as just `>` or `|`, and printed only `Usage:` on a usage error (#36).
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

1. Update the version in `plugin.json` and `.claude-plugin/plugin.json` (they must match; `python3 tools/validate_plugin.py` checks).
2. Move `[Unreleased]` entries under a new `[x.y.z] — YYYY-MM-DD` heading.
3. Commit: `chore(release): bump to vX.Y.Z`.
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
5. Push tag: `git push origin vX.Y.Z`.
