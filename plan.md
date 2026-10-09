# Restructuring Plan: uw-slides for Multi-Collaborator, Multi-Training Use

Status: in progress. WS0 done on branch `ws0-baseline-fixes` (see Progress). This document is self-contained so each workstream (WS) can be
handed to a separate agent/context window. Read **sections 1-4** (shared
context), then only the WS you are assigned.

---

## 1. Goal

Make the plugin reproducible and usable across many trainings and many
collaborators, while keeping what already works: the brand design system, the
fragment-per-slide architecture, the two-pass workflow, the accessibility
rules and the review skills.

Target workflow:

```
topic + audience + duration + slide count
   │  /uw-slides:plan-deck                  (LLM, conversational, approval gate)
   ▼
deck.yml + slides/*.md                      (briefs: message, layout, notes, owner, status)
   │  catalog slides resolved, not regenerated
   ▼
content/*.html                              (LLM fills layout slots; catalog slides copied)
   ▼
build → lint → design/a11y review → publish
```

Three levels at which a person can work: (0) topic, (1) briefs, (2) HTML.

## 2. Current state (verified facts)

Repository: `/home/arendta/git/aaarendt/uw-slides-plugin` (bash scripts + HTML, no deps except `python3` in `publish.sh`).

```
.claude-plugin/{plugin.json (v0.1.0), marketplace.json}
CLAUDE.md, README.md, LICENSE
skills/{new-deck,apply-visuals,accessibility-check,design-review,extract-to-markdown}/SKILL.md
templates/{build.sh, build-visuals.sh, publish.sh, SLIDES.md, VISUALS.md, AGENTS.md, CLAUDE.md,
           shared/{header,footer}.html, examples/{01-title,02-comparison}-example.html}
design-systems/{uw-brand,cloudbank-brand}/{DESIGN.md, colors_and_type.css, shared/header.html}
design-systems/uw-brand/fonts/   (45 TTFs, ~9.3 MB, copied into every deck)
references/{accessibility-requirements.md, markdown-schema.md}
```

Known problems (fix in WS0 unless noted):

1. `templates/build.sh` and `templates/build-visuals.sh` only match headings with `grep "^## [0-9]"`, so slide IDs starting with a letter are silently skipped. The README claims there is no required format beyond `## slide-id`.
2. Slide count is taken from headings, not built fragments. A missing fragment gives a warning and exit 0. `grep -c ... || echo 0` prints `0` twice when there is no match.
3. No checks for duplicate IDs, orphan fragments in `content/`, or `data-slide` not matching the filename.
4. Spacing docs conflict. `README.md` line ~144 says 4px base with `--space-8: 32px`; `CLAUDE.md` line ~109 says 8px base with `--space-8 = 64px`. Actual values: `design-systems/*/colors_and_type.css` uses 4px steps (`--space-8: 32px`, `--space-20: 80px`), but the deck-time `shared/header.html` doubles them (`--space-8: 64px`, `--space-16: 128px`, `--space-20: 160px`). Decide which is intended, document the relationship, and make the docs agree.
5. `README.md` lines ~204-205 reference `design-systems/uw-brand/templates/shared/{header,footer}.html`, which do not exist (actual path: `design-systems/<brand>/shared/header.html`, and `templates/shared/footer.html`). `CLAUDE.md` also shows a `templates/` dir under each brand that does not exist.
6. `new-deck` SKILL says it creates `README.md` from an inline snippet; there is no template file. `templates/shared/header.html` is byte-identical to `design-systems/uw-brand/shared/header.html` (duplicate; pick one source).
7. README says "LLM-agnostic" and "no Python/Node", but install/skills are Claude Code specific and `publish.sh` needs `python3`.
8. Hard-coded `~/.claude/plugins/local/uw-slides/...` paths in `skills/new-deck/SKILL.md`, `templates/AGENTS.md`, `README.md`, `CLAUDE.md`, `design-systems/uw-brand/DESIGN.md`.
9. UW header loads Open Sans from Google Fonts CDN (offline rooms fall back to system fonts); CloudBank loads all fonts from CDN.
10. Scaffold copies build scripts, header/footer and 9 MB of fonts into every deck; no version stamp, so decks drift from the plugin.
11. `.claude/settings.local.json` exists locally; confirm it is not tracked and add it to `.gitignore` if needed.
12. `references/markdown-schema.md` already defines a front-matter schema (`slide_id`, `title`, `layout`, `background`, ...). Extend it rather than creating a competing one.

## 3. Target architecture and decisions

### 3.1 Deck layout (new)

```
<deck>/
├── .uw-slides.json          # plugin version, brand, scaffold date, catalog pin
├── deck.yml                 # ordered slide list + deck metadata (replaces heading regex)
├── slides/<id>.md           # per-slide brief: front matter + key message/bullets/notes (human source of truth)
├── content/<id>.html        # generated or catalog-resolved fragments
├── content-with-visuals/    # pass 2 (unchanged)
├── assets/
├── shared/                  # header/footer (managed by update-deck)
├── OUTLINE.md               # generated read-only overview (from deck.yml + briefs); never hand-edited
└── build/ (ignored)
```

Legacy decks have a `SLIDES.md` instead of `deck.yml` + `slides/`. New decks do **not** get a `SLIDES.md` (see D11). Do not keep both as sources of truth.

### 3.2 Decisions (resolved from discussion)

| # | Decision |
|---|----------|
| D1 | Slide metadata lives in **separate files** (`slides/<id>.md` front matter), not in HTML comments. HTML is a regenerable artifact. |
| D2 | HTML carries only **generated provenance** as `data-` attributes: `data-layout`, `data-brief-hash`, `data-generated-by`. |
| D3 | Brief fields include `id, layout, layout_rationale, objective, owner, status (draft/review/done), duration, locked, use, params`. `locked: true` means the HTML is hand-edited and must not be regenerated. All per-slide data (including `use`/`params` for catalog slides) lives in the brief, not in `deck.yml`. |
| D4 | Order and deck metadata live in `deck.yml`; filename = `id` = `data-slide` (lint-enforced). |
| D5 | Layout choice is made by the planner from a closed **layout library** (`layout: auto` by default, user may override), with escape hatch `layout: custom` + `layout_intent`. |
| D6 | **Catalog slides** (finished, vetted, optionally parameterized) are referenced with `use: catalog/<id>` and copied by a resolver, never regenerated. Pinned by version; `eject` converts to a local locked slide. |
| D7 | Catalog is a **separate repo** (content, different owners/cadence). Until it exists, develop it under `catalog/` in this repo with the same structure. |
| D8 | Decks pin the plugin version (`.uw-slides.json`) and can be refreshed with an `update-deck` action; no silent following of latest. |
| D9 | Deterministic `lint.sh` is a required CI check; LLM `design-review`/`accessibility-check` remain for judgment. |
| D10 | Path assumptions removed: use `UW_SLIDES_HOME` (fallback to the repo location / `~/.claude/plugins/local/uw-slides`). |
| D11 | **`SLIDES.md` is phased out, not kept alongside `deck.yml`** (two sources of truth would drift). Transition: (a) builds use `deck.yml` when present and fall back to `SLIDES.md` for legacy decks; (b) new decks scaffold `deck.yml` + `slides/` and no `SLIDES.md`; (c) migration converts legacy decks; (d) the fallback is deprecated with a warning in v0.2.0 and removed in a later release (target v0.3.0). A one-page outline, if wanted, is **generated** (`OUTLINE.md`, read-only). The generation rules in the `SLIDES.md` template ("How to render this deck") move into the generation skill and schema docs, not into each deck. |

### 3.3 Decisions still open (ask the user before implementing the affected WS)

- ~~**O1 Parser constraint**~~ **Resolved: restricted YAML subset parsed by one stdlib-only `python3` script (`tools/deckparse.py`).** Rules:
  1. The subset must be valid YAML (never invent syntax), so PyYAML can replace the parser later without rewriting any file, and editor YAML tooling keeps working.
  2. Reject, don't guess: anything outside the subset (anchors, multi-line blocks, flow-style nesting, tabs, duplicate keys, nesting deeper than allowed) fails with file and line number. Tests include valid-YAML-but-unsupported fixtures that must fail.
  3. Grammar: flat `key: value` scalars (strings quoted or unquoted, integers, `true`/`false`; `yes/no/on/off` are plain strings), lists of scalars, and **one** level of nested map (`params:` in briefs, and `objectives:` as `id: text` in `deck.yml`).
  4. `deck.yml` holds flat deck metadata plus `slides:` as a plain ordered list of IDs (one per line). Per-slide data lives in the brief front matter (D3).
  5. Python 3 (stdlib only, no pip) becomes a requirement for lint, the staleness hash, the catalog resolver and `update-deck`. WS5 may keep a dependency-free `sed`/`awk` path in `build.sh` for reading the ID list; that is optional. Update the README's dependency claims accordingly when the parser lands.
  6. Revisit (switch to PyYAML) only if anchors, deeper nesting or multi-line strings become necessary.
- **O2 Runtime.** Keep homegrown `footer.html` navigation, or adopt reveal.js (vendored single JS/CSS) for scaling, presenter view with notes, overview and PDF export. Recommendation: evaluate in WS8, default to adopting.
- **O3 PPTX.** Is editable PPTX export required? Recommendation: defer; HTML + PDF first; briefs/layouts keep a future PPTX exporter possible.
- **O4 Fonts.** Subset to used weights, ship via release asset/LFS/submodule, or keep copying. Check Encode Sans licence (SIL OFL) before redistribution decisions.
- ~~**O5 Spacing scale**~~ **Resolved:** the 8px-base scale rendered by the deck headers is canonical (`--space-4` = 32px, `--space-20` = 160px). DESIGN.md, `colors_and_type.css` and README now match (WS0).

### 3.4 Progress

Update this checklist after each merge so new sessions know the current state.

- [x] WS0 Baseline fixes (branch `ws0-baseline-fixes`; slide heading rule: `## <kebab-case-id>`; `--strict` flag, default warn-and-skip for missing fragments; build scripts assemble output in a temp file)
- [ ] WS1 Versioning, stamping, paths
- [ ] WS2 Schemas (deck.yml, briefs)
- [ ] WS3 Layout library
- [ ] WS4 plan-deck skill
- [ ] WS5 Generation + deck.yml build
- [ ] WS6 Catalog + resolver
- [ ] WS7 Lint + CI
- [ ] WS8 Runtime/export
- [ ] WS9 Collaboration docs
- [ ] WS10 Series layout
- [ ] WS11 Migration + docs

WS0 follow-ups for later workstreams: `skills/new-deck/SKILL.md` has two sections numbered "3."; the new-deck skill and `templates/AGENTS.md` still contain hard-coded `~/.claude/plugins/local/uw-slides` paths (WS1).

## 4. Conventions for every workstream

- Surgical changes; do not edit files outside your scope. If you need a change elsewhere, note it in your report.
- Preserve backward compatibility: existing decks (SLIDES.md + `content/`) must keep building. New behavior is opt-in or falls back.
- Update directly related docs (README.md, CLAUDE.md, templates/AGENTS.md, SKILL.md files).
- Font-size rules from `CLAUDE.md` apply to any slide HTML you write (min 1.5rem, source lines `clamp(1rem, 1.1vw, 1.25rem)`).
- Slide fragments must use the scoped pattern `section[data-slide="<id>"]`.
- Validate by building a throwaway deck in `/tmp` (scaffold from templates, add 2-3 fragments, run the scripts). Clean up afterwards.
- Do not commit unless asked. When committing, include the `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.
- End your work with a short report: files changed, how verified, follow-ups, decisions needed.

## 5. Dependency graph

```
WS0 baseline fixes ──┬─► WS1 versioning/paths ──► WS10 series repo layout
                     ├─► WS2 schema ──┬─► WS3 layout library ──► WS4 plan-deck skill
                     │                ├─► WS5 generation + deck.yml build ──► WS11 migration
                     │                └─► WS6 catalog + resolver ───────────┘
                     ├─► WS7 lint + CI   (needs WS2 for brief checks; basic checks can start after WS0)
                     └─► WS8 runtime/export (independent after WS0)
WS9 collaboration docs: after WS2 and WS7
```

Parallelizable after WS0: WS1, WS2, WS7 (basic), WS8. After WS2: WS3, WS5, WS6. WS4 needs WS3 (layout catalogue) and WS6 (catalog descriptions).

---

## 6. Workstreams

### WS0. Baseline fixes and doc consistency

**Scope:** fix problems 1-7, 9 (documentation only), 11 in section 2. No new features.

**Read:** `templates/build.sh`, `templates/build-visuals.sh`, `templates/publish.sh`, `README.md`, `CLAUDE.md`, `skills/new-deck/SKILL.md`, `design-systems/*/colors_and_type.css`, `design-systems/*/shared/header.html`, `.gitignore`.

**Tasks:**
1. Build scripts: accept any `## <id>` heading that matches a valid slide ID (kebab-case, may start with a letter) but ignore non-slide headings; decide and document the rule (for example, only headings inside SLIDES.md after the intro, or a documented ID regex). Count slides actually built; exit non-zero on missing fragments (or add a `--strict`/default strict flag; keep a warning mode only if backward compat needs it). Fix the double-`0` count bug. Detect duplicate IDs. Warn about orphan files in `content/`.
2. Resolve the spacing-scale inconsistency (open question O5: ask the user, then update README, CLAUDE.md, DESIGN.md as needed).
3. Fix README "Global Defaults" paths; remove the nonexistent `templates/` dirs from CLAUDE.md structure.
4. Add `templates/README.md` (deck README) and have `new-deck` SKILL copy it instead of an inline snippet.
5. Remove the duplicate `templates/shared/header.html` or make it explicitly the neutral base; document which header `new-deck` uses.
6. Correct the README "LLM-agnostic / no Python" claims (state `python3` for `publish.sh` only).
7. Ensure `.claude/settings.local.json` is git-ignored.

**Acceptance:** build with a letter-prefixed ID works; missing fragment fails the build; correct count printed; docs agree on spacing; no references to nonexistent paths (`grep` verifies).

### WS1. Versioning, scaffold stamping, path independence

**Depends on:** WS0.

**Read:** `skills/new-deck/SKILL.md`, `templates/AGENTS.md`, `templates/CLAUDE.md`, `.claude-plugin/plugin.json`, files containing `claude/plugins` (grep).

**Tasks:**
1. `new-deck` writes `.uw-slides.json` (`plugin_version`, `brand`, `scaffolded_at`, `catalog` pin placeholder). Keep `.brand` for compatibility or fold it in (update all skills that read `.brand`).
2. Replace hard-coded `~/.claude/plugins/local/uw-slides` with `UW_SLIDES_HOME` plus documented fallback in skills, README, AGENTS.md, CLAUDE.md, DESIGN.md.
3. Deck-level `AGENTS.md` states the essential rules itself (or points to a pinned, vendored copy) instead of pointing outside the repo.
4. New skill/script `update-deck`: compares managed files (`build*.sh`, `publish.sh`, `shared/footer.html`, `shared/header.html`) with the pinned/current plugin version, shows a diff, and updates on confirmation; updates the stamp. Never touches `content/`, `slides/`, `assets/`.
5. Bump `plugin.json` to 0.2.0 when the restructuring lands; add `CHANGELOG.md`; document the tagging/release process.

**Acceptance:** scaffolded deck contains `.uw-slides.json`; no `~/.claude/plugins` literal remains except as the documented fallback; `update-deck` is idempotent and leaves user content untouched.

### WS2. Schemas: deck.yml and slide briefs

**Depends on:** WS0. Decision O1 is resolved (see section 3.3).

**Read:** `references/markdown-schema.md`, `templates/SLIDES.md`, `skills/extract-to-markdown/SKILL.md`, `templates/examples/*.html`.

**Tasks:**
1. Write `references/slide-schema.md` (extend, do not duplicate, `markdown-schema.md`; reconcile `slide_id` vs `id` and mark the old fields deprecated or mapped). Define the front matter: `id, layout, layout_rationale, objective, owner, status, duration, locked, use, params, section, notes` and the body sections (`# Key message`, columns/regions per layout, `## Notes`).
2. Define `deck.yml`: flat metadata (title, audience, duration, catalog pin), `objectives:` as an `id: text` map, and `slides:` as a plain ordered list of IDs. Per-slide `use`/`params`/`layout`/`owner`/`status` belong in the brief front matter, not here (D3, O1 rule 4).
3. Implement the restricted YAML subset from O1 as `tools/deckparse.py` (stdlib only), emitting JSON or shell-friendly output for ordered IDs, front matter and params. Include a test script with fixtures covering valid files, quoting/colon/empty-value edge cases, `yes/no` as strings, and valid-YAML-but-unsupported constructs that must fail with a file and line number.
4. Define the staleness hash (`data-brief-hash`): algorithm, which fields/body are hashed, how whitespace is normalized.
5. Add templates: `templates/deck.yml`, `templates/slides/_example.md`.
6. Relocate the generation rules from the "How to render this deck" section of `templates/SLIDES.md` into the schema doc (and, in WS5, the generation skill) so they apply to every deck and are no longer copied per deck. Rules to preserve: key message is the headline and the main shown text; bullets are spoken talking points, never rendered verbatim; "Note to self"/notes are never rendered; source lines render as a small footer citation; pass 1 uses no photographs or decorative icons and must look finished without images; default to one anchoring element per slide; consistent type scale, whitespace and gold accent. Map `## Notes` in briefs to the old "Note to self".
7. Document the SLIDES.md-to-new-schema mapping (needed by WS5 fallback and WS11 migration) and the deprecation timeline from D11.

**Acceptance:** schema doc is unambiguous; parser round-trips fixtures including edge cases (quotes, colons, empty values, missing fields yield clear errors).

### WS3. Layout library and catalogue

**Depends on:** WS2.

**Read:** `design-systems/uw-brand/DESIGN.md` (layout patterns, checklists), `templates/examples/*`, `references/accessibility-requirements.md`, CloudBank DESIGN.md for brand differences.

**Tasks:**
1. Define 8-12 layouts as slot-based HTML/CSS templates, brand-neutral via tokens: title, section divider, key-message, bullets/talking-points, two-column, comparison, big-number/stat, quote, exercise/activity, code/terminal, diagram, closing. Each: slots, constraints (max words/bullets), responsive behavior at 16:9 and 4:3.
2. Write `references/layouts.md`: for each layout a one-line description, **"use when / avoid when"**, slot list, example brief. This is what the planner reads; keep it compact.
3. Provide example fragments under `templates/layouts/<name>.html` that pass the font-size rules and a11y requirements.
4. Define `layout: custom` + `layout_intent` rules and when it is acceptable.
5. Variety rules for the planner (for example: no more than two consecutive identical layouts; stat-like message -> big-number).

**Acceptance:** each layout builds in a test deck in UW and CloudBank brands, no font under 1.5rem (except allowed exceptions), alt text/semantics correct, text fits at 16:9 and 4:3.

### WS4. `plan-deck` skill (+ re-plan)

**Depends on:** WS2, WS3; benefits from WS6 catalog descriptions.

**Read:** `references/slide-schema.md`, `references/layouts.md`, `catalog/catalog.yml` (if present), an existing SKILL.md for format (`skills/new-deck/SKILL.md`).

**Tasks:**
1. `skills/plan-deck/SKILL.md`: inputs (topic, audience, duration, slide count, source material path(s), brand). Ask questions only for missing essentials; otherwise state assumptions.
2. Steps: draft 2-4 learning objectives and confirm; map objectives to slides; pacing rules (about 4 min per content slide, an activity every 3-4 slides, recap, call to action); choose catalog slides first, then layouts, `custom` last; fill `layout_rationale`.
3. Write `deck.yml` and `slides/*.md` briefs. Mark any LLM-introduced factual claims in notes so a subject expert can verify them; prefer provided source material.
4. **Approval gate:** print an outline table (ID, key message, layout/catalog, minutes, objective) and stop for approval before any HTML is generated.
5. Re-plan operations: add/remove/merge/split slides, change duration or count; respect `locked`, `owner`, and `status: done`.

**Acceptance:** dry run on a sample topic yields valid schema files (checked by the WS2 parser), varied layouts, total minutes within target, every objective covered.

### WS5. Generation skill and deck.yml-driven build

**Depends on:** WS2 (and WS3 for layouts).

**Read:** `templates/build.sh`, `templates/build-visuals.sh`, `skills/apply-visuals/SKILL.md`, `references/slide-schema.md`, `references/layouts.md`.

**Tasks:**
1. `skills/generate-slides/SKILL.md`: reads `slides/<id>.md` (+ DESIGN.md + layout template), writes `content/<id>.html` with `data-layout`, `data-brief-hash`, `data-generated-by`; skips `locked: true` and `use:` catalog slides; reports stale (hash mismatch) slides and asks before overwriting.
2. Update `build.sh` and `build-visuals.sh` to read order from `deck.yml` (via `tools/deckparse.py`). If there is no `deck.yml`, fall back to the SLIDES.md heading logic from WS0 and print a **deprecation warning** pointing to the migration guide (D11).
3. Update `new-deck` so new decks scaffold `deck.yml` + `slides/` and **do not** create `SLIDES.md`; remove or replace `templates/SLIDES.md` (generation rules already moved in WS2). Update all skills that read `SLIDES.md` (`apply-visuals`, `design-review`, `accessibility-check`, `extract-to-markdown`, `templates/AGENTS.md`/`CLAUDE.md`, `VISUALS.md` template wording) to read `deck.yml`/`slides/` first and `SLIDES.md` only for legacy decks.
4. Add an `outline` script/skill step that generates the read-only `OUTLINE.md` (ID, key message, layout, minutes, owner, status) from `deck.yml` + briefs, with a "generated, do not edit" header.
5. Update `apply-visuals` to read briefs/`deck.yml` where relevant and preserve provenance attributes.
6. Update `extract-to-markdown` so it can also emit `slides/*.md` + `deck.yml` from an existing deck.

**Acceptance:** a deck with `deck.yml` builds in the correct order; a legacy `SLIDES.md` deck still builds but prints the deprecation warning; a newly scaffolded deck contains no `SLIDES.md`; `OUTLINE.md` is generated and reproducible; regenerating skips locked slides; changing a brief marks it stale in lint (WS7).

### WS6. Slide catalog and resolver

**Depends on:** WS2.

**Read:** `templates/examples/*`, `references/slide-schema.md`, `templates/shared/footer.html`, `templates/publish.sh` (image inlining paths).

**Tasks:**
1. Structure (under `catalog/` for now, extractable to its own repo): `catalog.yml` (id, description, tags, params with types/defaults, brand, version, status, owner), `slides/<id>/{slide.html, slide.md, assets/}`.
2. Kinds: verbatim, parameterized (`{{param}}` substitution, HTML-escaped), derived (agenda from `deck.yml`; implement as a small script).
3. `tools/resolve-catalog.sh` (or Python): for each `use:` entry, copy fragment to `content/<deck-id>.html`; rewrite `data-slide`, the scoped CSS selectors and the `aria-label` slide number to the deck slide ID; copy assets and fix relative paths so `publish.sh` still inlines them; validate required params; record `data-catalog="<id>@<version>"`.
4. Version pinning (`catalog` in `deck.yml`/`.uw-slides.json`); `eject` action that copies the resolved slide into the deck, sets `locked: true`, and removes `use:`.
5. Seed 5-6 slides: title, land acknowledgement, funding credit, agenda (derived), feedback, thank-you/contact. **Do not invent official acknowledgement or funding wording**: use placeholders and ask the user for approved text.
6. Document curation rules: owners, review, keep it to about 10-15 slides, framing slides only.

**Acceptance:** a deck referencing 3 catalog slides builds and publishes with correct styling, no ID collisions, images inlined; changing a param changes output deterministically; eject works.

### WS7. Deterministic lint and CI

**Depends on:** WS0 (basic checks); WS2 for brief checks.

**Tasks:**
1. `templates/lint.sh` (or `tools/lint.py`, stdlib only) with exit codes and machine-readable output. Checks: every `deck.yml`/SLIDES.md ID has a fragment and vice versa; `data-slide` equals the filename; no duplicate IDs; every fragment has `class="slide"` and `aria-label`; no font-size below 1.5rem except documented exceptions (source lines, labels); `<img>` has `alt`; stylesheet selectors are scoped to the slide; stale brief hash; `locked`/`status` summary; required catalog params present.
2. Contrast check for token pairs in the design systems (script over `colors_and_type.css` pairs defined in DESIGN.md).
3. GitHub Actions workflow template (`templates/.github/workflows/deck.yml`): build, lint, publish, upload `index-published.html` as an artifact (Pages optional, document it).
4. `status.sh` (or lint mode) printing a table: id, owner, status, locked, stale.
5. Document in the `design-review` and `accessibility-check` skills which checks are now deterministic (so the LLM skills focus on judgment).

**Acceptance:** fixtures with each defect type fail with a clear message; a clean deck passes; CI workflow runs locally via `act` or is statically valid YAML.

### WS8. Runtime and export (investigation first)

**Depends on:** WS0. Needs decision O2/O3.

**Tasks:**
1. Evaluate reveal.js (vendored, single JS/CSS) vs the current `footer.html`: scaling at 16:9/4:3, presenter view and speaker notes (briefs' `## Notes` rendered as `<aside class="notes">`), overview, print-to-PDF, fragment/step reveals, keyboard/touch, accessibility (focus, aria-live slide change), offline use, size, licence. Produce a short recommendation doc (`docs/runtime-evaluation.md`) with a prototype.
2. If adopting: keep the fragment pattern, scoped CSS and `section.slide` markup compatible; migrate `footer.html`; keep legacy footer as a fallback option.
3. PDF/PNG export script (Playwright, optional dependency, documented) for review artifacts and a visual baseline.
4. Notes rendering decision: notes from briefs shown only in presenter view, never on slides.

**Acceptance:** recommendation delivered; if adopted, existing example slides render without edits; PDF export produces one page per slide.

### WS9. Collaboration process

**Depends on:** WS2, WS7.

**Tasks:** `CONTRIBUTING.md` (branch/PR flow, who edits briefs vs HTML, how to lock a slide, regenerating on a branch only), PR template (preview link/artifact, lint passing, objective mapping), `CODEOWNERS` pattern mapping `slides/<id>.md` to owners, guidance on recording the model/prompt context in commit messages, licence/attribution notes for images and fonts (Encode Sans: SIL OFL; confirm UW brand asset terms).

**Acceptance:** a new collaborator can follow `CONTRIBUTING.md` from clone to preview in under 10 minutes on a clean machine (document prerequisites).

### WS10. Series/multi-training layout

**Depends on:** WS1 (and WS5/WS6 for full value).

**Tasks:**
1. Define a "training series" repo layout: shared brand/header/footer/fonts/catalog pin at the root, one folder per module/session (each with `deck.yml`, `slides/`, `content/`). Decide how modules share the build tooling (submodule/subtree/`UW_SLIDES_HOME`) and how fonts are shared (decision O4).
2. `training.yml`: title, audience, duration, objectives, prerequisites, presenters, variables (dates, URLs) substituted into catalog params and briefs, so reused modules need no hand-editing.
3. `new-deck`/`new-series` flows; document when to use which.

**Acceptance:** two modules in one series share tooling/fonts without copying 9 MB each and build independently.

### WS11. Migration and documentation

**Depends on:** WS5, WS6 (run last).

**Tasks:** migration guide for decks built with the old layout (what to run, what changes), extend `extract-to-markdown` to split SLIDES.md into briefs and `deck.yml` (one-shot `migrate-deck` flow that also stamps `.uw-slides.json` and keeps the old `SLIDES.md` in git history only), update `README.md`, `CLAUDE.md`, `templates/AGENTS.md`, and `templates/CLAUDE.md` for the new workflow, update `.claude-plugin/plugin.json` (skills list, version, keywords), write `CHANGELOG.md` (state the SLIDES.md deprecation and the planned removal release), tag release.

**SLIDES.md removal milestone (D11):** the legacy fallback ships deprecated in v0.2.0. Remove the fallback, `templates/SLIDES.md` leftovers and legacy wording in a later release (target v0.3.0), after at least one release with the warning and a working migration path. Track it as a separate issue.

**Acceptance:** an old deck migrates with a documented procedure, builds from `deck.yml`, and no longer needs `SLIDES.md`; docs have no stale path/command references and describe SLIDES.md only as legacy.

---

## 7. Suggested execution order

1. WS0 (single agent; unblocks everything). Resolve O5 with the user.
2. In parallel: WS1, WS2, WS8 investigation, WS7 basic checks.
3. In parallel: WS3, WS5, WS6.
4. WS4, WS7 brief checks, WS9.
5. WS10, WS11.

## 8. Sub-agent prompt template

```
You are working on workstream <WSn> of /home/arendta/git/aaarendt/uw-slides-plugin.
Read plan.md sections 1-4 and your workstream section (<WSn>) only.
Respect the conventions in section 4. Dependencies <list> are <done/not done>:
<paste any decisions made, e.g., O1 = python3 stdlib parser>.
Do the tasks, verify against the acceptance criteria using a throwaway deck in /tmp,
update directly related docs, do not commit, and finish with a short report
(files changed, verification, follow-ups, decisions needed).
```
