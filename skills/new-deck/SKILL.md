---
name: new-deck
description: Scaffold new UW presentation with fragment-based architecture
---

# New UW Presentation Deck (Fragment-Based)

## Purpose
Create a UW-branded presentation using a modular, LLM-first architecture where each slide is a self-contained HTML fragment.

## Usage
```bash
/uw-slides:new-deck <presentation-name>
/uw-slides:new-deck <presentation-name> --brand=cloudbank
```

The optional `--brand=<uw|cloudbank>` parameter selects the design system. Defaults to `uw`.

## Architecture Overview

This skill creates a **fragment-based** presentation:
- Each slide is a complete HTML `<section>` with inline scoped styles
- Build process is simple concatenation in the order listed in `deck.yml`
- Each slide has a brief in `slides/<id>.md` (message, layout, notes, owner, status); the HTML is generated from it
- Layouts come from the layout library (`references/layouts.md`), with `layout: custom` as the escape hatch
- Easy reordering: move a line in `deck.yml`

## Generated Directory Structure

```
<presentation-name>/
├── shared/
│   ├── header.html              # Design tokens, base styles
│   └── footer.html              # Navigation, closing tags
├── deck.yml                     # Deck metadata, objectives and slide order (source of truth for order)
├── .brand, .uw-slides.json      # Brand name and the plugin-version stamp (read by the other skills)
├── tools/                       # Vendored deckparse.py, lint.py and resolve-catalog.py
├── .github/                     # CODEOWNERS, pull request template, CI workflow
├── slides/                      # One brief per slide: slides/<id>.md (source of truth for content)
├── content/                     # Pass-1 slide fragments (generate-slides writes here)
├── content-with-visuals/        # Pass-2 slide fragments (apply-visuals writes here)
├── assets/
│   ├── images/
│   └── diagrams/
├── OUTLINE.md                   # Generated read-only overview (created by ./outline.sh)
├── VISUALS.md                   # Pass 2: per-slide visual additions
├── build.sh                     # Pass 1: concatenate content/ → build/index.html
├── outline.sh                   # Regenerate OUTLINE.md from deck.yml + slides/
├── build-visuals.sh             # Pass 2: concatenate content-with-visuals/ → build/index-with-visuals.html
├── publish.sh                   # Pass 3: inline images as base64 → build/index-published.html
└── README.md                    # User instructions
```

## Workflow

1. **Scaffold:** Run this skill to create directory structure
2. **Plan:** Run `/uw-slides:plan-deck` (drafts objectives, layouts and briefs, stops for approval), or edit `deck.yml` (order) and `slides/<id>.md` (one brief per slide) by hand
3. **Create slides:** Run `/uw-slides:generate-slides` (reads the briefs, writes `content/`)
4. **Build pass 1:** Run `./build.sh` → `build/index.html`
5. **Rehearse:** Present from `build/index.html`; revise the briefs, regenerate and rebuild as needed
6. **Plan visuals:** Edit `VISUALS.md` once content is settled
7. **Apply visuals:** Run `/uw-slides:apply-visuals` (LLM reads VISUALS.md, writes to `content-with-visuals/`)
8. **Build pass 2:** Run `./build-visuals.sh` → `build/index-with-visuals.html`
9. **Publish:** Run `./publish.sh` → `build/index-published.html` (all images inlined as base64 for a fully self-contained portable file)

## Slide Fragment Pattern

Each slide must follow this pattern:

```html
<section data-slide="NN-descriptive-name" 
         aria-label="Slide N: Title Here"
         class="slide">
  
  <!-- Content structure (any HTML the LLM designs) -->
  <div class="container">
    <h1>Title</h1>
    <p>Content...</p>
  </div>

  <!-- Scoped styles using attribute selector -->
  <style>
    section[data-slide="NN-descriptive-name"] {
      /* All styles scoped to this section only */
      background: var(--uw-spirit-purple);
      display: grid;
      grid-template-columns: 1fr 1fr;
      /* ... custom layout ... */
    }
    
    section[data-slide="NN-descriptive-name"] h1 {
      font-family: var(--font-display);
      /* ... custom typography ... */
    }
  </style>
</section>
```

## Key Constraints

**Required:**
- `data-slide` attribute with unique ID
- `aria-label` for accessibility
- `class="slide"` for navigation system
- All styles scoped with `section[data-slide="..."]` selector
- Follow UW brand colors (use CSS variables from header)
- Minimum 24px font size (WCAG 2.1 AA)
- 4.5:1 contrast ratio minimum

**Available CSS Variables (from header.html):**

For `--brand=uw`:
- Colors: `--uw-spirit-purple`, `--uw-husky-purple`, `--uw-spirit-gold`, `--uw-husky-gold-web`, `--uw-heritage-gold`, `--uw-white`, `--uw-black`, `--uw-gray-90`, etc.
- Fonts: `--font-display` (Encode Sans), `--font-display-wide`, `--font-display-compressed`, `--font-display-narrow`, `--font-display-condensed`, `--font-body` (Open Sans), `--font-mono`
- Spacing: `--space-1` (8px) through `--space-20` (160px); common: `--space-8` 64px, `--space-16` 128px, `--space-20` 160px

For `--brand=cloudbank`:
- Colors: `--cb-deep-navy`, `--cb-signal-blue`, `--cb-ink`, `--cb-mist`, `--cb-fog`, `--cb-white`, `--cb-black`, etc.
- Semantic aliases: `--bg-primary`, `--bg-surface`, `--text-body`, `--text-on-dark`, `--border-accent`, etc.
- Fonts: `--font-display` (Nunito), `--font-body` (Open Sans)
- Spacing: `--space-1` (8px) through `--space-20` (160px); common: `--space-8` 64px, `--space-16` 128px, `--space-20` 160px

**Design Freedom:**
- Layouts come from the library (`references/layouts.md`); `layout: custom` allows any HTML structure and CSS layout within the brand rules
- Within a slide, keep to the brand tokens and the type scale

## When User Requests a Slide

Slides are generated from briefs by `/uw-slides:generate-slides`. If the user asks for a new slide by conversation:

1. **Read `deck.yml` and the existing briefs** to understand the plan
2. **Ask clarifying questions** about the message and purpose
3. **Write `slides/<id>.md`** (front matter and `# Key message`; see `references/slide-schema.md`) and **add the ID to `deck.yml`** at the right position
4. **Run `/uw-slides:generate-slides <id>`** to create `content/<id>.html`
5. **Instruct user** to run `./build.sh` to rebuild

## Build and Preview

```bash
# Build presentation
./build.sh

# Preview in browser
open build/index.html
```

## Accessibility Checklist

Every slide must meet WCAG 2.1 Level AA:
- All images have `alt` text
- Text size ≥ 24px
- Contrast ratio ≥ 4.5:1
- Semantic HTML (`<h1>`, `<p>`, `<ul>`, etc.)
- Keyboard navigation supported (automatic via footer.html)
- `aria-label` on section

## Implementation

Scaffolding is done by one script, `<PLUGIN>/tools/new-deck.py`, not by copying files one at a time. Do **not** scaffold by hand: the script gives the same result every run and needs one permission instead of about twenty. It needs `python3` (standard library only), which the plugin's other tools already need.

### 1. Find the plugin directory

Paths written as `<PLUGIN>/...` are files in the uw-slides plugin, not in the deck. Find `PLUGIN` once. The first candidate whose `tools/new-deck.py` runs wins:

1. `$UW_SLIDES_HOME`, if set (`printenv UW_SLIDES_HOME`). Use this to point at a development checkout.
2. The plugin this skill was loaded from, two directories above this `SKILL.md` (`<PLUGIN>/skills/new-deck/SKILL.md`). Take the skill's path from your client, for example Claude Code's "Base directory for this skill", and resolve symlinks. This is where Claude Code, Codex, Copilot and other Agent Plugins clients install the plugin.
3. `~/.claude/plugins/local/uw-slides`, the legacy symlink install.

Do not read a file to confirm a candidate: step 2 fails with "can't open file" if the path is wrong, and then you try the next candidate. If none works, stop and ask the user where the plugin is.

### 2. Run the script

Run this one command from the directory where the deck folder should be created (the user's current directory), with `PLUGIN` written out as the literal absolute path:

```
python3 <PLUGIN>/tools/new-deck.py <presentation-name> --brand=<brand>
```

`--brand` defaults to `uw`; leave it out unless the user asked for another brand. Rules for the command, because Claude Code can only match an allow rule against literal text:

- **Never use shell variables** (`PLUGIN=... python3 $PLUGIN/...`), `cd`, `&&` or pipes. Write each path literally and run one command per call.
- Quote the presentation name if it contains spaces.

Recommended allow rules, for the project's or the user's `.claude/settings.json`. The plugin folder is version-numbered, so the rule uses a `*` for the path instead of a literal version:

```
Bash(python3 */tools/new-deck.py *)
Bash(printenv UW_SLIDES_HOME)
```

### 3. Report the result

The script prints a short summary and exits 0 on success. Relay it, including any `⚠` line, then show the next steps below.

- **Exit 1 with "already exists":** the script never touches an existing folder. Ask the user for a different name; do not delete or reuse the folder yourself.
- **Exit 1, any other message:** the script removed the folder it started. Relay the message; do not retry by hand.
- **Exit 2:** a usage error (bad `--brand`, missing name). Fix the command.
- **reveal.js warning:** the deck is complete. The download needs internet access; tell the user to run `./setup-reveal.sh` when they are online. Until then a manually installed copy at `assets/reveal/` also works.

### What the script does

For reference; do not repeat these steps by hand:

- Copies the build scripts (`build.sh`, `build-visuals.sh`, `lint.sh`, `status.sh`, `outline.sh`, `publish.sh`, `export.sh`, `setup-reveal.sh`), `VISUALS.md`, `shared/footer.html` and the brand's `shared/header.html`, the `.github/` collaboration and CI files, and the vendored `tools/deckparse.py`, `tools/lint.py` and `tools/resolve-catalog.py`. All `*.sh` files are made executable.
- For `--brand=uw`, copies the Encode Sans fonts to `assets/fonts/` (about 9 MB, so decks are self-contained). CloudBank decks load their fonts from the Google Fonts CDN.
- Writes `README.md` and `AGENTS.md` with the presentation name and brand filled in, `CLAUDE.md`, `.gitignore`, and `.brand` (the brand name, which other skills read; keep it git-tracked).
- Writes `deck.yml` (title set to the presentation name; slides `title` then `example-slide`) and the starter briefs `slides/title.md` and `slides/example-slide.md`, then validates them. There is no `SLIDES.md`, and no `content/` fragments: `/uw-slides:generate-slides` writes those.
- Writes `.uw-slides.json` with `plugin_version`, `brand`, `scaffolded_at`, `catalog` (null) and `plugin_dir`. `/uw-slides:update-deck` uses it to detect drift. `plugin_dir` lets the deck's `tools/resolve-catalog.py` find the catalog; it goes stale when the plugin updates (the cache folder is version-numbered) until `/uw-slides:update-deck` rewrites it, and it is machine-specific, so don't commit it to a repository shared between machines (the resolver ignores a path that doesn't exist).
- Creates the empty `content/`, `content-with-visuals/`, `assets/images/` and `assets/diagrams/` folders.
- Runs `setup-reveal.sh` to download reveal.js into `assets/reveal/`. These files should be git-tracked so the deck works offline afterwards. A failed download is reported as a warning and does not fail the scaffold.

## Next steps to show the user

After a successful run, tell the user:

```
✓ Created <brand> presentation: <presentation-name>/

Pass 1 — content and structure:
1. cd <presentation-name>
2. Run /uw-slides:plan-deck to plan the deck from a topic (or edit deck.yml and the briefs in slides/ by hand)
3. Run /uw-slides:generate-slides to create the slide HTML in content/
4. Build: ./build.sh
5. Preview: open build/index.html
6. Rehearse; revise the briefs, regenerate and rebuild until content is settled
7. Optional: ./outline.sh writes OUTLINE.md, a read-only overview

Pass 2 — visual additions (after content is settled):
1. Edit VISUALS.md to specify photos, icons, and diagrammatic accents
2. Run /uw-slides:apply-visuals
3. Build: ./build-visuals.sh
4. Preview: open build/index-with-visuals.html

Pass 3 — publish (portable, self-contained file):
1. Run: ./publish.sh
2. Share: build/index-published.html (all images inlined as base64)

PDF export (requires Playwright + Node):
1. ./export.sh → build/deck.pdf
2. Or open build/index.html?print-pdf in Chrome and print to PDF

Keyboard shortcuts in the browser (reveal.js):
  Arrow keys / Space  — navigate
  S                   — presenter view (speaker notes)
  Esc                 — slide overview
  ?                   — keyboard help

Each slide is a self-contained HTML fragment with inline scoped styles,
generated from its brief using the layout library.
```

Also tell the user to update `.github/CODEOWNERS` with real GitHub usernames once the slide plan is agreed (the `owner:` field in each brief is the reference).
