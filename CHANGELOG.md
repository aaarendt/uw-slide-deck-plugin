# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Versions follow semantic versioning: MAJOR.MINOR.PATCH. Deprecations are noted under the version they are introduced in; scheduled removals name the target version.

---

## [Unreleased]

## [0.7.0] — 2026-11-06

`/uw-slides:generate-slides` no longer asks permission for every command, read and write. New decks come with Claude Code permission rules, and `/uw-slides:update-deck` adds them to existing decks. **In existing decks, run `/uw-slides:update-deck`.** It shows the rules it will add and keeps everything already in your settings. The corrected `setup-reveal.sh` comes with it, so run `/uw-slides:update-deck` there once for both (see Fixed).

### Added
- `tools/test_setup_reveal_urls.py` checks that the three download URLs in `templates/setup-reveal.sh` exist on jsDelivr (HEAD requests). It is skipped when the CDN cannot be reached, and checks the local path the deck expects either way (#56).
- `tools/deckperms.py` writes the permission rules into a deck: `.claude/settings.json` (commit it) allows the deck's own commands (`python3 tools/deckparse.py`, `python3 tools/resolve-catalog.py resolve`, `python3 tools/lint.py`, `./build.sh`, `./build-visuals.sh`, `./outline.sh`, `./lint.sh`, `./status.sh`, `printenv UW_SLIDES_HOME`) and edits to `content/` and `slides/`; `.claude/settings.local.json` (this computer only, added to `.gitignore`) allows reading the plugin's folder, where the skills read layouts, brand rules and schemas. It adds only missing rules, keeps everything else, leaves a settings file that is not valid JSON untouched, and `--check` shows what it would add. `tools/test_deckperms.py` covers it.
- `/uw-slides:new-deck` runs it, so a new deck has the rules from the start. It prints how many it wrote.
- `tools/test_skill_commands.py` reads every command out of the `SKILL.md` files and fails unless each one is covered by a permission rule or is on a short list of commands that are meant to ask (`resolve-catalog.py eject`, `./publish.sh`, `./export.sh`, `./setup-reveal.sh`, `git rm`). It also fails on a compound command (`&&`, `;`, pipes, `$VAR`, redirects), because Claude Code checks each part and one unmatched part makes the whole command ask. A command added to a skill without a rule now fails CI instead of bringing the prompts back.
- README "Permission prompts" explains the rules, which commands still ask (`./publish.sh`, `./export.sh`, `git`, `resolve-catalog.py eject`), and the two user-level rules for the plugin's own scripts (`new-deck.py`, `deckperms.py`).

### Changed
- Every skill now says to run each command exactly as written, as one command with nothing appended. In a live run Claude added `2>/dev/null; echo "exit: $?"` to `printenv UW_SLIDES_HOME`, and the `$?` made an otherwise allowed command ask. The skills also say to check for a file with the Glob or Read tool instead of `ls` or `test` in the shell, and `generate-slides` no longer redirects the resolver's output (`2>&1`).
- `/uw-slides:update-deck` checks the permission rules and offers to add them, in the same confirmation as the managed files. It treats them as add-only: they are not managed files and are never overwritten.
- `.gitignore` in new decks lists `.claude/settings.local.json`.

### Fixed
- `setup-reveal.sh` downloads the speaker-notes plugin from `dist/plugin/notes.js`, where reveal.js 6.x ships it. It used the 5.x path `plugin/notes/notes.js`, which returns 404 for 6.0.2, so the script stopped (`set -e`) after `reveal.min.js` and `reveal.min.css` and left `assets/reveal/plugin/notes/notes.js` missing. The file is still saved as `assets/reveal/plugin/notes/notes.js`, so `footer.html`, `publish.sh`, `export.sh` and `new-deck.py` are unchanged. Without it the footer's `RevealNotes` reference throws, `Reveal.initialize` never runs and the deck is a black screen. **In existing decks, run `/uw-slides:update-deck`, then `./setup-reveal.sh`.**
- The README's manual-download instructions for the notes plugin use the correct URL.
- `/uw-slides:update-deck` now manages `setup-reveal.sh` (#41), so existing decks receive changes to it.

### Why
- The earlier fix for permission prompts (#51) covered only `/uw-slides:new-deck`, by replacing about 20 commands with one script. `/uw-slides:generate-slides` still asked about the `deckparse.py` and resolver commands (which no rule was shipped for), about reading the plugin's files from outside the deck, and about writing each slide, so a 15-slide deck could mean 30 or more prompts. The skills also named an allow rule only in prose, and only for `deckparse.py`.

## [0.6.2] — 2026-11-05

New decks get an up-to-date `README.md` that links back to the uw-slides repository. Nothing else changes, so existing decks don't need `/uw-slides:update-deck` for this release.

### Changed
- The `README.md` that `/uw-slides:new-deck` writes into each deck is rewritten for the current workflow. It links to the uw-slides repository as the deck's source and to its install, update, catalog, brief-format, layout, brand and accessibility pages, and says where the plugin version is recorded. It now covers what it left out: the brand review and the accessibility check (which `/uw-slides:generate-slides` runs, and which can be run again), `./lint.sh` and `./status.sh`, catalog slides, replacing the two starter slides, `plan-deck replan`, the presenter keys and where speaker notes come from, keeping a deck up to date with `/uw-slides:update-deck`, and which files to leave alone. It no longer has you run `./build.sh` after `generate-slides`, which already builds. A "Live deck" line is there to replace with the GitHub Pages link. Existing decks keep their README (`/uw-slides:update-deck` never touches `*.md` files); copy `templates/README.md` from the plugin to replace it, then put the deck's name and brand back in.

## [0.6.1] — 2026-11-05

A deck without pass-2 visuals failed in CI: git does not keep empty folders, so the CI checkout had no `content-with-visuals/` and `./build-visuals.sh` stopped with "content-with-visuals/ not found". **In existing decks, run `/uw-slides:update-deck`** to get the fixed `build-visuals.sh`.

### Fixed
- `build-visuals.sh` treats a missing `content-with-visuals/` like an empty one: it notes it and builds every slide from `content/`, instead of failing. This is what CI hit on a fresh checkout of a deck with no visuals.
- `/uw-slides:new-deck` puts a `.gitkeep` file in each folder it creates empty (`content/`, `content-with-visuals/`, `assets/images/`, `assets/diagrams/`), so a clone of a new deck has them.

### Added
- `tools/test_new_deck.py` commits a new deck to git, clones it as CI does and runs the CI build steps (`./build.sh --strict`, `./build-visuals.sh --strict`, `./publish.sh --site`), with and without the `.gitkeep` files.

## [0.6.0] — 2026-11-05

Finished decks can now go live on GitHub Pages: the deck's CI workflow deploys every push to `main` to `https://<owner>.github.io/<repo>/`, where anyone can open the deck and present it, speaker view included. The published file also works on its own now; it used to show every slide in one stack wherever the deck's `assets/` folder was missing. And `./export.sh` makes a PDF again; it had failed on every run. **In existing decks, run `/uw-slides:update-deck`** to get the new `publish.sh`, `export.sh` and CI workflow (the last two are now managed files, so the update offers them), then set Settings → Pages → Source to GitHub Actions in the deck's repository.

### Added
- The deck CI workflow (`.github/workflows/deck.yml`) deploys the deck to GitHub Pages on every push to `main` (and when run by hand), in a separate `deploy-pages` job with the `pages`/`id-token` permissions and `github-pages` environment it needs. One-time setup is Settings → Pages → Source: GitHub Actions. Until then, or while Pages publishes from a branch, the job skips the deploy with a notice instead of failing; if it cannot read the Pages settings it deploys anyway and lets the deploy report the problem. Pull requests build, lint and upload a preview artifact but never deploy.
- `./publish.sh --site` also writes `build/site/`: the published page as `index.html` plus the local files it still links to, copied with their paths rewritten from `build/` to the site (`../assets/fonts/X.ttf` becomes `assets/fonts/X.ttf`). For UW decks that is the Encode Sans files, so the headings keep their font on Pages; images and reveal.js are inlined and not copied. Relative paths keep working under a Pages project URL (`/<repo>/`). Inline scripts are never rewritten, and the folder is rebuilt from scratch each run. Checked by serving the site from a subfolder in Chrome: Encode Sans loads (the browser fetched only the one weight the slides use), navigation and speaker view work. This folder is what CI deploys and what the `deck` artifact now contains.
- `./export.sh --notes` adds a page of speaker notes after each slide.
- `tools/test_publish.py` (stdlib only, no network): runs `templates/publish.sh` on a small fake deck and checks the inlining, exact copying of backslashes, the end-tag guard, the fallback to `build/index.html`, the dependency report and the `--site` folder.
- README "8. Share it" describes the three ways to share a deck (GitHub Pages, one file, PDF), with the Pages setup and its limits: a Pages site is public even from a private repository (private needs a paid GitHub plan), the speaker notes can be read by anyone, and web fonts need the viewer online.

### Fixed
- `publish.sh` inlines the reveal.js stylesheet (`<link rel="stylesheet">` becomes `<style>`), reveal.js and the speaker-notes plugin (`<script src>` becomes an inline `<script>`), resolving paths from `build/` as it does for images. `http(s):` and `data:` URLs are left alone, and a missing local file still prints "not found" and keeps its link. The "unknown type" warnings for the two script files are gone. Contents are copied as is, and a `</script` or `</style` inside an inlined file is written as `<\/script` / `<\/style` so it cannot close the element early. The file grows by about 240 KB. Checked in Chrome with only the published file in an empty folder, opened from `file://` and over HTTP: one slide at a time, arrow keys, the "3 / 15" counter, and speaker view (S) with notes, synced in both directions.
- `publish.sh` publishes `build/index.html` when `build/index-with-visuals.html` is missing, instead of failing, so decks without visuals no longer need `./build-visuals.sh` first (the CI workflow's publish step failed on this). It warns when `build/index.html` is newer than `build/index-with-visuals.html`, which means pass 2 was not rebuilt.
- `export.sh` passed `npx playwright pdf` options it does not have (`--wait-for-load-state`, `--landscape`, `--format`), so it stopped with "unknown option" and never wrote a PDF. It now drives Playwright from a short script: 1920×1080 pages (16:9, the size the layouts are checked at, instead of A4), slide backgrounds printed, the fonts the slides use embedded, and a tagged PDF (reading order and alt text for screen readers). It waits for reveal.js and the fonts before printing, and warns when a font file failed to load or Google Fonts could not be reached, because the PDF would then embed a substitute. It finds Playwright in the deck's `node_modules` or the global npm folder, falls back to an installed Google Chrome if Playwright's Chromium is missing, and refuses unknown options. Checked on a UW and a CloudBank deck: 15 pages, Encode Sans embedded, UW purple background printed, and the warnings for a missing `assets/fonts/` and for no internet.

### Changed
- `export.sh` and `.github/workflows/deck.yml` are now managed files, so `/uw-slides:update-deck` updates them in existing decks (it shows the diff and any of your own edits it would remove before asking). `.github/workflows/deck.yml` is a different file from the deck's own `deck.yml`, which stays untouched.
- The deck CI workflow runs `./build-visuals.sh --strict` before publishing and uploads `build/site/` as the `deck` artifact (unzip and open `index.html`) instead of the single file.
- `publish.sh` ends by listing what the published file still depends on: local files it did not inline (UW decks: the 45 Encode Sans files in `../assets/fonts/`) and hosts it needs internet for (Google Fonts, used for Open Sans and the CloudBank fonts). Fonts are not inlined; offline, or without `assets/fonts/` next to the file, the browser uses a system font. `build/site/` and GitHub Pages carry the font files.
- `README.md`, the deck `README.md` and `AGENTS.md`, `CONTRIBUTING.md`, `CLAUDE.md` and `/uw-slides:new-deck` no longer call the published file "fully self-contained"; they say what is inlined, and describe `--site`, Pages and the PDF export.

## [0.5.0] — 2026-11-05

Fixes the CloudBank slides that overlapped or ran off the screen on laptop-size displays: all 13 now fit at every size from 1920×1080 down to 1024×768. The CloudBank catalog also changes shape: a new slide on where to get help, a diagram on `cb-what-is` showing that CloudBank sits between you and the clouds, and `cb-why-choose` now covers what `cb-programs` did. **The catalog version is now 3.0.0 because `cb-programs` was removed:** a deck that uses it needs the change under Removed. Revised catalog slides reach a deck the next time you run `/uw-slides:generate-slides`. No build scripts or tools changed, so decks don't need `/uw-slides:update-deck` for this release.

### Added
- Catalog slide `cb-getting-help` (CloudBank brand, parameterized): "You don't have to figure out the cloud alone", the places to get help, ordered by how people look for it. "Learn on your own" lists the video tutorials (Cloud 101 and the monthly Cloud Clinics, cloudbank.org/video-tutorials) and the CloudBank Catalog (cloudbank.org/cloudbank-catalog); "Ask a person" lists the monthly office hours on Zoom (10–11 am Pacific) and the community forum (community.cloudbank.org); a band at the bottom gives help@cloudbank.org. An optional `next-office-hours` param shows the next session's date, since there is no stable page listing upcoming sessions. Checked at 1920×1080, 1600×1200, 1440×900, 1366×768, 1280×720 and 1024×768.

### Changed
- The catalog version is now 3.0.0: `cb-programs` was removed (see Removed), so the major version changes, and `cb-getting-help` was added. Decks pinned to 2.x keep working unless they use `cb-programs`; see Removed for the fix.
- Catalog slide `cb-what-is` 1.1.0 is now "CloudBank: A Managed Service to Simplify Cloud Access", built around one diagram that shows CloudBank is not a cloud itself. A Researcher (with an ACCESS or NAIRR Pilot award) points to CloudBank, a navy box listing what it does behind teal arrows: opens your accounts, pays from your award, tracks your spending. The box stands on the edge of a shaded "Commercial clouds" panel ("where your work runs"), and lines fan out from it to AWS, Google Cloud, Microsoft Azure and IBM Cloud. Who runs it (UC San Diego (SDSC), UC Berkeley and UW eScience, funded by NSF since 2019) is one line at body size underneath; the 2025 award and the NAIRR role moved to the speaker notes, since `cb-by-the-numbers` and `cb-nairr` cover them. The headline uses CloudBank's own "managed services" wording rather than "gateway", which in ACCESS usually means a science gateway. The diagram is slide text with drawn arrows and icons, so it follows the font-size minimum and reads in order with a screen reader. Checked at 1920×1080, 1600×1200, 1440×900, 1366×768, 1280×720 and 1024×768.
- Catalog slide `cb-why-choose` 2.0.0 is now "What you get with a CloudBank account", merging in the former `cb-programs`. Two columns of four headed items with line icons. "Billing, handled for you": no credit card, one bill across several clouds, a spending cap, dollars rather than credits. "Accounts, handled for you": accounts set up after onboarding, one login (ACCESS credentials) to each cloud, collaborators managed in one place, and another cloud added later, from the ACCESS resource pages. Both columns say what CloudBank adds over going to a provider directly; general cloud capabilities stay on `cb-why-cloud`. The help and training items of `cb-programs` are covered by `cb-getting-help`. Checked at 1920×1080, 1600×1200, 1440×900, 1366×768, 1280×720 and 1024×768.
- `CLAUDE.md`'s font-size rules no longer contradict each other. "Use at least `2vw` for body text" and a body range of "1.6–2.2vw" are replaced by the rule the CloudBank fixes followed: body text should reach its maximum at about 1920px wide (the maximum in px ÷ 19.2, so `1.7vw` for a `2rem` maximum), with the body range now `clamp(1.5rem, 1.55–1.8vw, 1.875–2rem)`. A higher vw keeps body text above the minimum on laptop screens, which caused the overflow fixed below. The headline rule is unchanged.

### Removed
- Catalog slide `cb-programs`, merged into `cb-why-choose` (see Changed), which keeps the CloudBank catalog within its 10 to 15 slide guideline. A deck that used it fails to resolve that slide ("catalog slide metadata not found"); its existing `content/<id>.html` is kept. Remove the slide from `deck.yml` (and add `cb-why-choose` if the deck doesn't have it), or keep the old slide by replacing `use: catalog/cb-programs` in its brief with `locked: true` and a `# Key message` line, as eject would have.

### Fixed
- Four CloudBank catalog slides overlapped or ran off the screen below 1920×1080, failing the fit check in `references/layouts.md` §7 (1920×1080, 1600×1200, 1280×720, 1024×768); all 13 CloudBank slides now pass it, also at 1440×900 and 1366×768. Each `clamp()` now reaches the 1.5rem floor on laptop screens instead of staying above it, with the same maximum, so the slides look the same at 1920×1080.
  - `cb-nairr` 1.1.0: the right column ran under the Sources line and off the bottom of the slide, so the "Teaching?" box overlapped the source links. Each step's title now sits on the same line as its text, and the Request step reads "reviewers match it to CloudBank" (was "to cloud through CloudBank").
  - `cb-rule-of-thumb-costs` 1.1.0: the $730 callout overlapped the prices line or fell off the slide. The price column is narrower, and two rows are shorter: "Laptop-class virtual machine" (was "Virtual machine with laptop power") and "NVIDIA A10G GPU machine", "Spot: about half. Ask for quota first." (was "Machine with an NVIDIA A10G GPU", "Spot: about half. Request GPU quota first.").
  - `cb-why-cloud` 1.0.1: at 1366×768 and smaller the vertically centred grid overflowed upwards into the "Why cloud?" heading. The grid now uses `align-content: safe center`.
  - `cb-by-the-numbers` 1.0.1: at 1280×720 the Accelerate row overlapped the Source line.
- The catalog table in `README.md` listed 6 of the 13 CloudBank slides. It now lists all of them, in catalog order.

## [0.4.0] — 2026-11-03

The CloudBank catalog grows to 13 slides, enough to build a standard CloudBank talk from catalog slides alone: a title slide, the case for cloud, what CloudBank offers and how to apply through ACCESS or the NAIRR Pilot, usage figures and rule-of-thumb costs. `/uw-slides:new-deck` now scaffolds a deck with one command. The catalog version is now 2.1.0. In existing decks, run `/uw-slides:update-deck` once to get the fixed resolver.

### Added
- Catalog slide `cb-rule-of-thumb-costs` (CloudBank brand, verbatim): "Rule-of-thumb cloud costs", round-number AWS on-demand prices (US East, October 2026) for a laptop-class VM (10¢/hour), a workstation ($1/hour), an A10G GPU machine ($1/hour, spot about half), hot storage (2.3¢/GB/month), cold archive (0.1¢/GB/month) and data egress (9¢/GB), each with an example, plus a callout that a $1/hour machine left on for a month costs about $730.
- Catalog slide `cb-by-the-numbers` (CloudBank brand, parameterized): "CloudBank by the numbers" for October 2025 to October 2026. Three headline stats (292 research projects, $2.24M allocated to research, 78 CloudBank Classroom courses), research awards by tier with average award (Explore 234 at $4,423, Discover 56 at $19,689, Accelerate 2 at $52,094), and the top three research fields plus 40 more. Every figure is a param defaulting to the current value, so decks can show newer figures without ejecting.
- Catalog slide `cb-nairr` (CloudBank brand, verbatim): "CloudBank through the NAIRR Pilot", the second route to a CloudBank account. Four labelled differences from ACCESS (AI focus, everyone on the project U.S.-based, cash awards, longer monthly review) and three numbered steps to request CloudBank through NAIRR (prepare: cost estimate, grant number, CVs, ACCESS account; request: three-page proposal at nairrpilot.org; onboard within 1–2 weeks), with a pointer to NAIRR Classroom projects for educators. The NSF portal screenshot from the source slide is not included. `slide.md` notes which claims come from the NAIRR Pilot pages and which from the slide owner.
- Catalog slide `cb-research-and-classroom` (CloudBank brand, verbatim): "Two ways to use CloudBank", a table comparing CloudBank Research (cloud accounts for research projects, through an ACCESS or NAIRR Pilot allocation) and CloudBank Classroom (a JupyterHub for teaching, through an Explore ACCESS allocation), with the two logos as column headers.
- Catalog slide `cb-why-cloud` (CloudBank brand, parameterized): a general "Why cloud?" motivation slide with six headed items and original line icons: bring compute to the data, scale up on demand, run in parallel, use and deploy LLMs, share reproducible environments, host research services. Example services are named in the speaker notes only. An optional `lead` param adds a talk-specific line under the heading.
- Catalog slide `cb-what-weve-heard` (CloudBank brand, verbatim): a dark "The friction" slide with four paraphrased researcher quotes (no account without a credit card, no time to learn it all, setup different on every platform, an opaque $12K bill), labelled as paraphrased. Each quote is answered by a later CloudBank slide.
- Catalog slide `cb-title` (CloudBank brand, parameterized): the CloudBank title slide, with the same params as `uw-title` (`title`, `subtitle`, `presenter`, `affiliation` defaulting to "CloudBank", `date`). A CloudBank deck can now be assembled entirely from catalog slides, starting with a title (#42).
- `tools/new-deck.py` scaffolds a deck in one command: `python3 <PLUGIN>/tools/new-deck.py <name> [--brand=uw|cloudbank]`. It does everything `/uw-slides:new-deck` used to do with about twenty separate commands (templates, brand header and footer, fonts for `uw`, the vendored tools, `.github/` files, `.brand`, `.uw-slides.json`, `deck.yml` and the starter briefs), validates the result and runs `setup-reveal.sh`. A failed reveal.js download is a warning, not a failure. It refuses to touch an existing folder, rejects names that are not safe as a folder name, removes the folder it created if a step fails, and makes every `*.sh` executable (`setup-reveal.sh` and `export.sh` were not executable in the plugin). Tests: `tools/test_new_deck.py`, including a check that its managed-files list matches `/uw-slides:update-deck`.
- README section "Update to a new version": how to update the plugin in Claude Code (`claude plugin update`, `/plugin`, turning on auto-update, `/reload-plugins`), Codex, GitHub Copilot CLI and linked-skill installs, then how to update each deck with `/uw-slides:update-deck`. The release process in this file and `CONTRIBUTING.md` now say that users receive changes only when the version changes, and add publishing a GitHub release.

### Changed
- The catalog version is now 2.1.0: seven CloudBank slides were added and `cb-title` changed (see Added and the line below). Nothing was removed, so decks pinned to 2.0.0 keep working.
- Catalog slide `cb-title` 1.1.0 carries the logos and award credit NSF requires: the CloudBank and NSF logos with "NSF Awards: 1925001 & 2505560", and a Deep Navy band of white partner logos (San Diego Supercomputer Center, UC San Diego, University of Washington, UC Berkeley, Strategic Blue). The background changes from Deep Navy to white so the full-colour logos read. The logos ship in the slide's `assets/` folder, the first catalog slide to use it; the resolver copies them into the deck and `publish.sh` embeds them. The `affiliation` default changes from `"CloudBank"` to empty, since the logo is on the slide. Params are otherwise unchanged, so decks pick this up on their next resolve.
- `/uw-slides:new-deck` runs that script instead of copying files one by one, so Claude Code asks for permission once instead of about twenty times, and the result is the same every run, in seconds and with few tokens. The README documents the allow rule `Bash(python3 */tools/new-deck.py *)`; the `*` stands in for the version-numbered plugin folder (#50).
- Every skill's "Plugin directory" section now says to write paths literally and never use shell variables (`PLUGIN=... $PLUGIN/...`), which Claude Code cannot match against an allow rule (#50).

### Fixed
- The deck's `tools/resolve-catalog.py` rewrites only the root `<section>`'s `aria-label` when it resolves a catalog slide. It used to rewrite every `aria-label` in the fragment, which would have replaced the labels inside a slide, such as the partner logo list on `cb-title` 1.1.0, with the slide's own label.

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

Users receive a release when the version in `plugin.json` changes, not when commits are pushed. Claude Code compares that version with the installed one, so changes merged to `main` without a version bump stay invisible to `claude plugin update` and auto-update, and a merged version bump reaches users straight away, before any tag exists. Merge release-worthy changes, then release them together.

1. Update the version in `plugin.json` and `.claude-plugin/plugin.json` (they must match; `python3 tools/validate_plugin.py` checks).
2. Move `[Unreleased]` entries under a new `[x.y.z] — YYYY-MM-DD` heading, with a one-paragraph summary that says whether users need to run `/uw-slides:update-deck` in existing decks.
3. Commit: `chore(release): bump to vX.Y.Z`, on a `release/vX.Y.Z` branch, and merge it with a pull request.
4. Tag the merge commit: `git tag -a vX.Y.Z -m "Release vX.Y.Z" <merge-commit>`.
5. Push tag: `git push origin vX.Y.Z`.
6. Publish a GitHub release from the tag, with the summary and the version's changelog sections as its description. People who watch the repository for releases are notified.

How users install updates is documented in the README, [Update to a new version](README.md#update-to-a-new-version).
