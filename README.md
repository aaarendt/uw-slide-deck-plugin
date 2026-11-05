# UW Slides

A plugin for Claude Code (and other coding agents) that turns a topic into a University of Washington or CloudBank branded slide deck. It plans the slides with you, writes them, and builds a presentation you open in a browser.

![A title slide built with UW Slides: "Cloud Computing for Researchers" in white on UW purple, with presenter, affiliation and date](docs/images/uw-title-slide.png)

- **Plans before it writes.** You describe the talk; the plugin drafts objectives and a slide-by-slide plan, and stops for your approval before writing any slides.
- **On brand and accessible.** Slides follow the UW or CloudBank design system and WCAG 2.1 AA, and two checks review a finished deck against both.
- **Easy to revise.** Each slide comes from a short text brief. Change a brief and regenerate that slide; slides you have edited by hand are never overwritten.
- **Ready-made slides.** Title, agenda, funding, feedback and closing slides, and the standard CloudBank introduction, come from a shared [catalog](#catalog-slides).

You need Claude Code (or [another supported agent](#other-agents)), `python3` (standard library only, nothing to install) and a web browser.

---

## Install

In your terminal:

```bash
claude plugin marketplace add aaarendt/uw-slide-deck-plugin
claude plugin install uw-slides@uw-slide-deck
```

Inside Claude Code the same commands start with `/plugin`: `/plugin marketplace add aaarendt/uw-slide-deck-plugin`, then `/plugin install uw-slides@uw-slide-deck`. The plugin's commands all start with `/uw-slides:`.

Installed an earlier version with a symlink? See [Upgrading from the symlink install](#upgrading-from-the-symlink-install). Already installed? See [Update to a new version](#update-to-a-new-version).

### Other agents

**Codex**

```bash
codex plugin marketplace add aaarendt/uw-slide-deck-plugin
codex plugin add uw-slides@uw-slide-deck
```

Ask for a skill by name, for example "use the uw-slides new-deck skill to scaffold my-talk".

**GitHub Copilot CLI** (follows GitHub's [plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference); not tested yet)

```bash
copilot plugin marketplace add aaarendt/uw-slide-deck-plugin
copilot plugin install uw-slides@uw-slide-deck
```

**OpenCode and other agents that read a skills directory.** Clone the repository, link each skill into the skills directory, and point `UW_SLIDES_HOME` at the clone:

```bash
git clone https://github.com/aaarendt/uw-slide-deck-plugin ~/src/uw-slide-deck-plugin
mkdir -p ~/.config/opencode/skills
for s in ~/src/uw-slide-deck-plugin/skills/*/; do ln -s "${s%/}" ~/.config/opencode/skills/; done
export UW_SLIDES_HOME=~/src/uw-slide-deck-plugin   # add to your shell profile
```

The same loop works for `~/.agents/skills` or any other skills directory. Skills keep their plain names there (`new-deck`, not `uw-slides:new-deck`).

---

## Update to a new version

New versions are listed in the [changelog](CHANGELOG.md) and on the [releases page](https://github.com/aaarendt/uw-slide-deck-plugin/releases). To be told about each one, choose **Watch → Custom → Releases** on the repository's GitHub page.

Updating takes two steps: update the plugin once, then update each deck you are still working on.

### 1. Update the plugin

**Claude Code.** In your terminal:

```bash
claude plugin update uw-slides@uw-slide-deck
```

This fetches the latest marketplace listing and installs the new version, or reports that you already have the latest one. `claude plugin list` shows which version you have. Inside Claude Code you can do the same from `/plugin`: on the **Installed** tab, open `uw-slides` and choose **Update now**.

- A session that is already running keeps the version it started with. Start a new session, or run `/reload-plugins` in the open one.
- `claude plugin marketplace update` on its own only refreshes the listing; it does not update the installed plugin.
- To get new versions automatically, run `/plugin`, go to the **Marketplaces** tab, select `uw-slide-deck` and choose **Enable auto-update**. It is off by default for marketplaces other than Anthropic's. With it on, Claude Code updates the plugin in the background after a session starts and tells you to run `/reload-plugins`.
- The plugin's folder name includes its version, so the first `/uw-slides:new-deck` after an update asks for permission again unless you added the allow rule in [Create the deck](#1-create-the-deck).

**Codex** (not tested yet). Refresh the marketplace, then check the installed version:

```bash
codex plugin marketplace upgrade uw-slide-deck
codex plugin list
```

If the list still shows the old version, install it again with `codex plugin add uw-slides@uw-slide-deck`. Start a new session to load it.

**GitHub Copilot CLI** (follows GitHub's [plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference); not tested yet):

```bash
copilot plugin marketplace update uw-slide-deck
copilot plugin update uw-slides
```

**OpenCode and other linked-skill installs.** Pull the clone; the linked skills read from it, so they update with it:

```bash
git -C ~/src/uw-slide-deck-plugin pull
```

Restart the agent to load the new skills. If a release adds a skill, run the linking loop from [Other agents](#other-agents) again; links that already exist report `File exists`, which is harmless.

### 2. Update each deck

Each deck keeps its own copies of the build scripts, the brand header and footer, and the Python tools, so it keeps working even when the plugin changes. After updating the plugin, open each deck you are still working on in Claude Code and run:

```
/uw-slides:update-deck
```

It lists the files that differ from the new version and asks before replacing them. It never touches your briefs, slides, `deck.yml` or images. It also records where the new version is installed, which the catalog resolver needs: until you run it, the resolver may report that it can't find the catalog.

Catalog slides come from the installed plugin, so new and revised catalog slides reach a deck the next time you run `/uw-slides:generate-slides`. Read the [changelog](CHANGELOG.md) first if a release changes a catalog slide you use.

Decks you have finished presenting don't need updating: a built deck keeps working with the files it has.

---

## Make your first deck

You work in Claude Code: type the `/uw-slides:` commands, or just ask in plain words ("rebuild the deck", "publish it"). The skills run the build and check scripts for you. The first time Claude Code wants to run each script it asks for permission; choose the option not to ask again, and from then on it runs them on its own. The only terminal steps are starting Claude Code (steps 1 and 2).

### 1. Create the deck

In your **terminal**, go to the folder where you keep your talks and start Claude Code:

```bash
cd ~/talks
claude
```

Then in **Claude Code**:

```
/uw-slides:new-deck my-talk
```

For a CloudBank deck, add `--brand=cloudbank`. This creates a `my-talk/` folder with the build scripts, the brand's styles and fonts, and the presentation runtime ([reveal.js](https://revealjs.com/), downloaded once, so this step needs internet access; offline, the deck is still created and you run `./setup-reveal.sh` later).

Creating the deck is a single command (`tools/new-deck.py` in the plugin), so Claude Code asks for permission once. The plugin's folder is named after its version, so a "don't ask again" answer stops matching after a plugin update. To allow it for good, add this rule to `permissions.allow` in `~/.claude/settings.json`:

```json
"Bash(python3 */tools/new-deck.py *)"
```

### 2. Reopen Claude Code inside the deck

The other commands run from inside the deck folder, so quit Claude Code and start it there:

```bash
cd my-talk
claude
```

### 3. Choose the slides

There are two ways to fill the deck. Pick by how much new content the talk needs.

**Plan a new talk with Claude.** For a talk with its own content:

```
/uw-slides:plan-deck "Cloud computing for researchers" --duration=45
```

Without a topic, it asks you for the essentials first. It drafts learning objectives, chooses a layout and writes the content for every slide, using [catalog slides](#catalog-slides) where they fit, then shows you the plan. Ask for changes or approve it. Nothing is written as HTML until you approve. This is the step that uses the most tokens.

**Assemble it from the catalog.** For a talk made mostly of standard slides, such as a CloudBank introduction, skip planning. List the slides in `deck.yml` and give each a short brief that names its catalog slide. For a CloudBank deck:

```yaml
# deck.yml
title: "CloudBank for Researchers"
slides:
  - title
  - what-is
  - programs
  - process
  - thank-you
```

```markdown
<!-- slides/title.md -->
---
id: title
use: catalog/cb-title
params:
  title: "CloudBank for Researchers"
  presenter: "Jane Doe"
---
```

```markdown
<!-- slides/what-is.md -->
---
id: what-is
use: catalog/cb-what-is
---
```

```markdown
<!-- slides/thank-you.md -->
---
id: thank-you
use: catalog/thank-you
params:
  presenter: "Jane Doe"
  email: "jdoe@uw.edu"
---
```

A brief needs only `id` and `use:`, plus `params:` for slides that take them (each slide's params are in [`catalog/README.md`](catalog/README.md)). new-deck starts every deck with two placeholder slides, `title` and `example-slide`: replace them in `deck.yml` and delete `slides/example-slide.md`. You can write these files yourself or ask Claude Code to ("make this deck the cb-title, cb-what-is, cb-why-choose, cb-process and thank-you catalog slides"); either way it costs few or no tokens.

If you include the `funding` slide, set its params: its defaults are placeholders, and the resolver warns while one still shows. For a few slides of your own among the catalog ones, write their briefs with a `layout:` instead of `use:` (see [`references/slide-schema.md`](references/slide-schema.md)); step 4 then writes only those.

### 4. Write the slides

```
/uw-slides:generate-slides
```

If the deck has catalog slides, this first copies them into the deck and fills in their params, and passes on any warnings (a placeholder you still need to set, for example). It then writes each slide that uses a layout from its brief. If every slide is a catalog slide, it only copies them. Finally it builds the presentation (`build/index.html`), and then runs the brand review and the accessibility check and reports what they found.

### 5. Look at it

Open `build/index.html` in your browser, or ask Claude Code to open it. See [Presenting](#presenting) for the keys.

### 6. Revise

- **Change a slide:** edit its brief in `slides/`, then run `/uw-slides:generate-slides` again. It writes new slides, leaves unchanged ones alone, asks before replacing a slide whose brief changed, and rebuilds.
- **Reorder:** move lines in the `slides:` list in `deck.yml` and ask Claude Code to rebuild.
- **Bigger changes** (add, remove, merge or split slides, change the length): `/uw-slides:plan-deck replan "make it 30 minutes"`.
- **Edit a slide's HTML by hand:** set `locked: true` in its brief so it is never regenerated.
- **Check the deck again:** `/uw-slides:design-review` and `/uw-slides:accessibility-check`.

Ask "which slides are out of date?" at any point for the status of every slide.

### 7. Add visuals (optional)

The first pass uses only layout, type and color. To add photos, diagrams and icons, describe them per slide in `VISUALS.md`, then:

```
/uw-slides:apply-visuals
```

It edits copies of the slides in `content-with-visuals/` and builds `build/index-with-visuals.html`. Slides you didn't list are unchanged, and the first-pass slides are never modified.

### 8. Share it

Ask Claude Code to **"publish the deck"**. This makes `build/index-published.html`, a single file with the images and the presentation runtime (reveal.js) built in, which you can email, upload or put on a web page on its own. Fonts are not built in: Open Sans and the CloudBank fonts load from Google Fonts, so they need internet access, and UW decks show the Encode Sans headings only where the deck's `assets/fonts/` folder sits next to the file. Elsewhere the browser uses a system font instead; the slides still work. `publish.sh` lists what the file still needs at the end of its output. Ask for a PDF and it runs the PDF export, which needs [Playwright](https://playwright.dev/) (`npm install -g playwright && npx playwright install chromium`).

### Running the scripts yourself

Everything the skills build or check is a plain script in the deck folder, so you or a colleague can rebuild a deck without an agent, or in CI:

| Script | What it does |
|--------|--------------|
| `./build.sh` | Builds `build/index.html` from `content/` in `deck.yml` order (`--strict` fails on missing slides) |
| `./build-visuals.sh` | Builds `build/index-with-visuals.html`, using `content-with-visuals/` where a slide has visuals |
| `./publish.sh` | Makes the single-file `build/index-published.html` (images and reveal.js inlined; fonts are not) from `build/index-with-visuals.html`, or from `build/index.html` if there is none |
| `./export.sh` | Writes `build/deck.pdf` (needs Playwright) |
| `./lint.sh` | Quick automatic checks: missing slides, alt text, font sizes, stale briefs |
| `./status.sh` | Lists every slide and whether it is up to date |
| `./outline.sh` | Refreshes `OUTLINE.md`, a read-only overview of the deck |
| `./setup-reveal.sh` | Downloads reveal.js again, if the download in step 1 failed |

Resolving catalog slides by hand is described in [Using a catalog slide](#using-a-catalog-slide).

---

## Presenting

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `S` | Presenter view (current and next slide, speaker notes, timer) |
| `Esc` | Overview of all slides |
| `F` | Fullscreen |
| `B` | Blank the screen |
| `?` | All keyboard shortcuts |

**Speaker notes** come from the `## Notes` section of a slide's brief. They appear only in presenter view.

---

## Skills

| Skill | What it does |
|-------|--------------|
| `/uw-slides:new-deck <name>` | Create a deck folder (`--brand=cloudbank` for CloudBank) |
| `/uw-slides:plan-deck` | Plan the deck from a topic: objectives, layouts and the content of every slide, with an approval step before any HTML. `replan "<change>"` changes an existing plan |
| `/uw-slides:generate-slides` | Write the slides from their briefs. Skips locked slides and asks before replacing slides whose brief changed |
| `/uw-slides:apply-visuals` | Add the photos, diagrams and icons described in `VISUALS.md` |
| `/uw-slides:design-review` | Check the deck against the brand guidelines |
| `/uw-slides:accessibility-check` | Check the deck against WCAG 2.1 AA |
| `/uw-slides:update-deck` | Bring a deck's scripts and tools up to date with the installed plugin. Never touches your slides or briefs |
| `/uw-slides:extract-to-markdown` | Turn an existing HTML deck into `deck.yml` and briefs; `--migrate` converts a deck that still uses `SLIDES.md` |

---

## What's in your deck folder

| | Files |
|---|---|
| **You edit** | `deck.yml` (title, objectives and slide order) · `slides/<id>.md` (one brief per slide: key message, talking points, sources, speaker notes, layout) · `VISUALS.md` (pass-2 visuals) · `assets/images/` |
| **Generated** (rebuilt, don't edit) | `content/` (one HTML file per slide) · `content-with-visuals/` · `build/` (the finished presentation) · `OUTLINE.md` (overview, refreshed by `./outline.sh`) |
| **Scripts** | `build.sh` · `build-visuals.sh` · `publish.sh` · `export.sh` · `lint.sh` · `status.sh` · `outline.sh` · `setup-reveal.sh` |
| **Leave alone** | `shared/` (brand styles and runtime) · `tools/` (copies of the plugin's Python tools) · `assets/fonts/`, `assets/reveal/` · `.uw-slides.json`, `.brand` |

A brief's **key message** becomes the slide's headline. **Talking points** are what you say, not text on the slide. **Notes** are speaker notes. The full brief format is in [`references/slide-schema.md`](references/slide-schema.md), and the 12 layouts are described in [`references/layouts.md`](references/layouts.md).

A slide ID is lowercase letters, digits and single hyphens (`why-cloud`) and matches its brief's file name. Keep the deck in git, including `assets/reveal/`, so it works offline.

When the plugin is updated, run `/uw-slides:update-deck` in each deck to pick up the new scripts and tools; see [Update to a new version](#update-to-a-new-version).

---

## Catalog Slides

The catalog is a set of pre-made, vetted slides that any deck can include by ID instead of writing them from scratch. They keep slides that should read the same in every talk consistent across decks.

| ID | What it is | Brand |
|----|-----------|-------|
| `uw-title` | Title slide: title, subtitle, presenter, affiliation, date | uw |
| `funding` | Funding credit: agency, grant ID, grant title (set them in the brief) | uw |
| `agenda` | Agenda built from the deck's own slides, sections and durations | any |
| `feedback` | Session feedback prompt with an optional survey link | any |
| `thank-you` | Closing slide with presenter and contact details | any |
| `cb-title` | Title slide: title, subtitle, presenter, affiliation, date | cloudbank |
| `cb-why-cloud` | Why use the cloud for research: six things it makes possible | cloudbank |
| `cb-what-weve-heard` | Four paraphrased researcher quotes about the friction of cloud | cloudbank |
| `cb-eligibility` | Who can lead a project; good and poor fits | cloudbank |
| `cb-what-is` | What CloudBank is and who runs it | cloudbank |
| `cb-research-and-classroom` | The two offerings side by side: Research and Classroom | cloudbank |
| `cb-why-choose` | What you get with a CloudBank account | cloudbank |
| `cb-award-tiers` | Grant award tiers (Explore, Discover, Accelerate) | cloudbank |
| `cb-process` | Steps from cost estimate to working in the cloud | cloudbank |
| `cb-nairr` | CloudBank through the NAIRR Pilot, and how it differs from ACCESS | cloudbank |
| `cb-by-the-numbers` | Usage figures for a stated period (projects, dollars, classrooms) | cloudbank |
| `cb-rule-of-thumb-costs` | Round-number cloud prices, and what a machine left on costs | cloudbank |
| `cb-getting-help` | Where to get help: videos, office hours, forum, help email | cloudbank |

Every slide in the catalog has been checked and is ready to use. The `funding` slide needs your award's details: its agency, grant ID and grant title default to `PLACEHOLDER` values, and the resolver warns until you set them. **Brand** limits where a slide is offered: `cb-` slides only in CloudBank decks, `uw` slides only in UW decks, `any` everywhere.

### Using a catalog slide

`/uw-slides:plan-deck` picks catalog slides for you when one fits a planned slide. To add one by hand, write `use: catalog/<id>` in the slide's brief instead of `layout:`, with `params:` for the fields you want to fill:

```markdown
---
id: title
use: catalog/uw-title
params:
  title: "Cloud Computing for Researchers"
  presenter: "Jane Doe"
  date: "November 3, 2026"
---
```

Catalog slides are copied, not generated. `/uw-slides:generate-slides` copies them into the deck for you and reports any warnings. Run it again after changing a catalog slide's params, or, for `agenda`, after changing slide titles, sections or durations.

Without an agent, run the resolver yourself:

```bash
python3 tools/resolve-catalog.py resolve . --catalog=<plugin>/catalog
```

You can usually leave out `--catalog`: `/uw-slides:new-deck` and `/uw-slides:update-deck` record where the plugin is installed in the deck's `.uw-slides.json` (`plugin_dir`), and the resolver reads it. After a plugin update that path is stale until you run `/uw-slides:update-deck`; if the resolver says it can't find the catalog, do that, or pass `--catalog=<plugin>/catalog`, where `<plugin>` is where the plugin is installed (it differs by agent and changes with each version, so don't save it in scripts). With `UW_SLIDES_HOME` set you can also leave out `--catalog`.

To change a catalog slide beyond its params, eject it. This keeps the slide in your deck as a locked, hand-edited slide and removes the link to the catalog:

```bash
python3 tools/resolve-catalog.py eject . <slide-id> --catalog=<plugin>/catalog
```

Each slide's params, defaults and notes are in [`catalog/README.md`](catalog/README.md). To add or change a catalog slide, see [`catalog/CURATION.md`](catalog/CURATION.md).

---

## Brands

| Brand | Look | Guidelines |
|-------|------|------------|
| `uw` (default) | Husky Purple and Spirit Gold, Encode Sans and Open Sans | [`design-systems/uw-brand/DESIGN.md`](design-systems/uw-brand/DESIGN.md) |
| `cloudbank` | Deep Navy and Signal Blue, Nunito and Open Sans | [`design-systems/cloudbank-brand/DESIGN.md`](design-systems/cloudbank-brand/DESIGN.md) |

Choose the brand when you create the deck (`/uw-slides:new-deck my-talk --brand=cloudbank`). The other skills read it from the deck's `.brand` file.

To change colors, spacing or type for one deck only, edit that deck's `shared/header.html`. The design tokens are listed in each brand's `colors_and_type.css`.

---

## Troubleshooting

**A skill asks where the plugin is, or uses old templates**
- An earlier install may still be in the way. Follow [Upgrading from the symlink install](#upgrading-from-the-symlink-install), and check that `UW_SLIDES_HOME` isn't set (`echo $UW_SLIDES_HOME`).

**"Catalog not found" when resolving catalog slides**
- You ran the resolver by hand and the plugin has moved or been updated since the deck was created. Run `/uw-slides:update-deck` to refresh the recorded location, run `/uw-slides:generate-slides`, which finds the plugin itself, or pass `--catalog=<plugin>/catalog` as shown in [Using a catalog slide](#using-a-catalog-slide).

**A slide is missing from the built deck**
- `./status.sh` shows which slides have no HTML yet. Run `/uw-slides:generate-slides` to copy catalog slides and generate the others.
- The build skips missing slides with a warning, so a half-finished deck still builds. `./build.sh --strict` fails instead.

**Slides are in the wrong order**
- The order is the `slides:` list in `deck.yml`, top to bottom, not the file names.

**Images don't show**
- Image paths are relative to `build/index.html`, so go up one level: `<img src="../assets/images/photo.jpg" alt="...">`.

**Fonts look wrong**
- UW decks need the Encode Sans files in `assets/fonts/` (copy them from the plugin's `design-systems/uw-brand/fonts/` if they're missing). CloudBank decks and Open Sans load from Google Fonts, so they need internet access. A published file (`build/index-published.html`) sent on its own has no `assets/fonts/`, so UW headings fall back to a system font there.

**The deck doesn't run, or presenter view (`S`) doesn't open**
- reveal.js is missing: run `./setup-reveal.sh` in the deck folder (it needs internet access). Offline, download `reveal.min.js`, `reveal.min.css` and `plugin/notes/notes.js` from `https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/` into `assets/reveal/`.

**A build script fails or warns about `deckparse.py`**
- The error gives the file and line of the problem in `deck.yml` or a brief.
- If the deck has no `tools/deckparse.py`, run `/uw-slides:update-deck` to add it.
- If a script won't run: `chmod +x *.sh`.

---

## Upgrading from the symlink install

Earlier versions were installed by symlinking a checkout to `~/.claude/plugins/local/uw-slides`, usually with a folder marketplace called `uw-slides-local` and sometimes with `UW_SLIDES_HOME` set. Leaving any of these in place next to the new install gives you two copies of the skills, and `UW_SLIDES_HOME` overrides the installed copy, so the skills keep reading your checkout. To switch:

```bash
claude plugin marketplace remove uw-slides-local     # also uninstalls the plugin it supplied
mv ~/.claude/plugins/local/uw-slides ~/.claude/plugins/local/uw-slides.off   # or delete it
unset UW_SLIDES_HOME                                 # and remove it from your shell profile
claude plugin marketplace add aaarendt/uw-slide-deck-plugin
claude plugin install uw-slides@uw-slide-deck
```

`claude plugin marketplace list` should then show `uw-slide-deck` and no `uw-slides-local`. Your checkout and your decks are not touched. Decks you already made keep working; run `/uw-slides:update-deck` in each to pick up the current scripts and tools.

---

## For plugin developers

See also [CONTRIBUTING.md](CONTRIBUTING.md) and [CLAUDE.md](CLAUDE.md), which covers the architecture, the slide HTML conventions and the font-size rules.

### Working on the plugin

Clone the repository and keep the marketplace install for everyday use. Two settings point Claude Code at your checkout while you test a change:

- `UW_SLIDES_HOME=/path/to/checkout` makes the skills read templates, design systems, the catalog and tools from your checkout. It takes precedence over the installed copy, so set it only in the terminal where you are testing.
- `claude --plugin-dir /path/to/checkout` also loads the skills' own instructions (`SKILL.md`) from your checkout. You need this when you change a skill. Disable the installed copy while you do (`/plugin disable uw-slides@uw-slide-deck`), so you don't have two sets of the same skills.

The older symlink install still works, but isn't needed for either.

### How the plugin is packaged

The repository is a single [Agent Plugins v1.0.0](https://agent-plugins.org/specification) plugin named `uw-slides`. The root `plugin.json` is the portable manifest (read by Codex and Copilot); `.claude-plugin/plugin.json` carries the same metadata for Claude Code, which doesn't read the portable one. The marketplace `uw-slide-deck` is in `.claude-plugin/marketplace.json` (Claude Code and Copilot) and `.agents/plugins/marketplace.json` (Codex). `python3 tools/validate_plugin.py` checks all of them.

### How skills find the plugin

An installed plugin lives in a cache that differs by agent, for example `~/.claude/plugins/cache/...` or `~/.codex/plugins/cache/...`. Each skill finds the plugin's templates, design systems and tools by checking, in order:

1. `$UW_SLIDES_HOME`
2. the plugin the skill was loaded from (two directories above its `SKILL.md`)
3. `~/.claude/plugins/local/uw-slides`

New decks get their own copies of `tools/deckparse.py`, `tools/lint.py` and `tools/resolve-catalog.py`, so building a deck never needs the plugin. The deck scripts fall back to `$UW_SLIDES_HOME/tools/` and `~/.claude/plugins/local/uw-slides/tools/` when a deck has no copy; without a parser they read the `slides:` list unvalidated.

### Changing the defaults for new decks

New decks are copied from the plugin's templates, so editing these changes every future deck:

```
design-systems/uw-brand/shared/header-reveal.html        # UW header (tokens, fonts, base styles)
design-systems/cloudbank-brand/shared/header-reveal.html # CloudBank header
templates/shared/footer-reveal.html                      # reveal.js setup (all brands)
templates/*.sh                                           # deck scripts
templates/deck.yml, templates/slides/, templates/VISUALS.md, templates/AGENTS.md
```

Existing decks pick up changes to the scripts, shared files and tools with `/uw-slides:update-deck`.

### Adding a brand

1. Create `design-systems/<name>-brand/` with `DESIGN.md` (guidelines), `colors_and_type.css` (tokens) and `shared/header-reveal.html` (tokens, font loading and base styles; copy an existing brand's and modify it).
2. Use `--brand=<name>` when creating a deck.

---

## License

MIT
