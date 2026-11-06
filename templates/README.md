# [Presentation Name]

[BRAND_NAME] presentation made with [uw-slides](https://github.com/aaarendt/uw-slide-deck-plugin), a plugin for Claude Code and other coding agents that builds branded, accessible HTML slide decks. The plugin version this deck uses is recorded in `.uw-slides.json`.

**Live deck:** once GitHub Pages is on (see [Share](#share)), the deck is at `https://<owner>.github.io/<repo>/`. Replace this line with the link.

## Working on this deck

You need the uw-slides plugin installed in your agent; see [Install](https://github.com/aaarendt/uw-slide-deck-plugin#install). Then open this folder in Claude Code and run the `/uw-slides:` commands below, or ask in plain words ("rebuild the deck", "check accessibility"). The scripts also run without an agent; see [Scripts](#scripts).

### 1. Choose the slides

- **Plan a talk:** `/uw-slides:plan-deck "<topic>" --duration=45` drafts the objectives, a layout and the content for every slide, and stops for your approval before any HTML is written.
- **Or assemble it from the catalog:** list slides in `deck.yml` and give each a brief with `use: catalog/<id>` (and `params:` where the slide takes them). The catalog has ready-made title, agenda, funding, feedback and closing slides, plus CloudBank slides; see the [catalog](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/catalog/README.md).

The deck starts with two placeholder slides, `title` and `example-slide`. Replace them in `deck.yml` and delete `slides/example-slide.md`.

### 2. Write the slides

```
/uw-slides:generate-slides
```

This copies in any catalog slides, writes each other slide from its brief into `content/`, builds `build/index.html`, refreshes `OUTLINE.md`, then runs the brand review and the accessibility check and reports what they found.

### 3. Look at it and revise

Open `build/index.html` in a browser (keys under [Present](#present)).

- **Change a slide:** edit its brief in `slides/<id>.md`, then run `/uw-slides:generate-slides` again. It leaves unchanged slides alone and asks before replacing one whose brief changed.
- **Reorder:** move lines in the `slides:` list in `deck.yml`, then rebuild (`./build.sh`).
- **Bigger changes** (add, remove, merge or split slides, change the length): `/uw-slides:plan-deck replan "make it 30 minutes"`.
- **Edit a slide's HTML by hand:** first set `locked: true` in its brief, so it is never regenerated.
- **Check it:** `/uw-slides:design-review` (brand guidelines) and `/uw-slides:accessibility-check` (WCAG 2.1 AA) run with every generate; run them again any time. `./lint.sh` is a quick automatic check, and `./status.sh` lists which slides are out of date.

### 4. Add visuals (optional)

The first pass uses only layout, type and color. To add photos, diagrams and icons, describe them per slide in `VISUALS.md`, then run `/uw-slides:apply-visuals`. It writes edited copies to `content-with-visuals/` and builds `build/index-with-visuals.html`; the first-pass slides are never changed.

## Share

- **GitHub Pages** (to present from any computer): commit the whole deck, including `assets/reveal/` and, for UW decks, `assets/fonts/`, and push it to GitHub. In the repository, set Settings → Pages → Source to **GitHub Actions**, then push again or re-run the "Deck CI" workflow. Every push to `main` then deploys the deck to `https://<owner>.github.io/<repo>/`. Until Pages is on, the workflow builds and checks the deck and skips the deploy with a notice. A Pages site is public, even from a private repository, and anyone can read the speaker notes.
- **One file** (to email or upload): `./publish.sh` writes `build/index-published.html`, with images, reveal.js and the speaker-notes plugin built in. Fonts are not: web fonts need internet access, and UW decks show the Encode Sans headings only where `assets/fonts/` sits next to the file (otherwise a system font is used). `./publish.sh --site` also writes `build/site/`, the folder CI puts on Pages, which works on any web server.
- **PDF** (handouts): `./export.sh` writes `build/deck.pdf`, one 16:9 page per slide with the fonts embedded (`--visuals` for the pass-2 build, `--notes` for a page of speaker notes after each slide). Export with internet access. It needs Playwright: `npm install -g playwright && npx playwright install chromium`.

## Present

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `S` | Presenter view: current and next slide, speaker notes, timer |
| `Esc` | Overview of all slides |
| `F` | Fullscreen |
| `B` | Blank the screen |
| `?` | All keyboard shortcuts |

Speaker notes come from the `## Notes` section of each brief and appear only in presenter view.

## Scripts

Everything the commands build or check is a plain script, so anyone can rebuild the deck without an agent (CI runs the same scripts):

| Script | What it does |
|--------|--------------|
| `./build.sh` | Builds `build/index.html` from `content/` in `deck.yml` order (`--strict` fails on missing slides) |
| `./build-visuals.sh` | Builds `build/index-with-visuals.html`, using `content-with-visuals/` where a slide has visuals |
| `./publish.sh` | Writes `build/index-published.html` (`--site` also writes `build/site/`) |
| `./export.sh` | Writes `build/deck.pdf` (needs Playwright) |
| `./lint.sh` | Quick checks: missing slides, alt text, font sizes, stale briefs |
| `./status.sh` | Lists every slide and whether it is up to date |
| `./outline.sh` | Refreshes `OUTLINE.md`, a read-only overview of the deck |
| `./setup-reveal.sh` | Downloads reveal.js again, if `assets/reveal/` is missing |

Every script takes a deck folder as an argument (`./build.sh path/to/deck`). They need `python3` (standard library only), except `export.sh`, which needs Node.js and Playwright.

## Keep it up to date

When the plugin has a new version, update it (see [Update to a new version](https://github.com/aaarendt/uw-slide-deck-plugin#update-to-a-new-version)), then run `/uw-slides:update-deck` here. It shows which scripts, shared files and tools differ from the new version and asks before replacing them; it never touches your briefs, slides, `deck.yml` or images. Catalog slides refresh the next time you run `/uw-slides:generate-slides`. A deck you have finished presenting doesn't need updating.

## What's in this folder

| | Files |
|---|---|
| **You edit** | `deck.yml` (title, audience, objectives, slide order) · `slides/<id>.md` (one brief per slide: key message, talking points, source, speaker notes, layout) · `VISUALS.md` (pass-2 visuals) · `assets/images/`, `assets/diagrams/` |
| **Generated** (don't edit) | `content/` (one HTML file per slide) · `content-with-visuals/` · `build/` (the finished presentation; not committed) · `OUTLINE.md` |
| **Leave alone** | `shared/` (brand styles and runtime) · `tools/` (copies of the plugin's Python tools) · `assets/fonts/`, `assets/reveal/` · `.uw-slides.json`, `.brand` · the scripts · `.github/` (CI and review settings) |
| **For agents** | `AGENTS.md`, `CLAUDE.md` |

A brief's **key message** becomes the slide's headline. **Talking points** are what you say, not text on the slide. A slide ID is lowercase letters, digits and single hyphens (`03-approach`) and matches its brief's file name.

## Learn more

- [uw-slides README](https://github.com/aaarendt/uw-slide-deck-plugin#readme): the full guide, including troubleshooting
- [Brief and `deck.yml` format](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/references/slide-schema.md) and [the 12 layouts](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/references/layouts.md)
- [Catalog slides and their params](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/catalog/README.md)
- [Brand guidelines for this deck](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/design-systems/[BRAND]-brand/DESIGN.md) and [accessibility requirements](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/references/accessibility-requirements.md)
- [Changelog](https://github.com/aaarendt/uw-slide-deck-plugin/blob/main/CHANGELOG.md): what changed in each plugin version
