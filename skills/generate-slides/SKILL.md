---
name: generate-slides
description: Resolve catalog slides and generate content/<id>.html slide fragments from slides/<id>.md briefs using the layout library. Skips locked slides, reports stale slides and asks before overwriting.
---

# Generate Slides (Pass 1)

## Purpose

Turn the briefs in `slides/<id>.md` (ordered by `deck.yml`) into HTML fragments in `content/<id>.html`. The brief is the source of truth; the HTML is a regenerable artifact that records which version of the brief it came from.

This skill **generates** layout slides and **resolves** catalog slides (`use: catalog/<id>`). Catalog slides are copied from the plugin's catalog by `tools/resolve-catalog.py`, never generated; this skill runs the resolver for you (step 2), so the user never needs to know the catalog path.

This skill replaces the old "read SLIDES.md and write slides by conversation" step. Legacy decks that only have `SLIDES.md` are not handled here: migrate them first (mapping in `<PLUGIN>/references/slide-schema.md`, section 6), or keep writing fragments by hand.

## Plugin directory

Paths written as `<PLUGIN>/...` are files in the uw-slides plugin, not in the deck. Resolve `PLUGIN` once per invocation. The first match wins, and `<PLUGIN>/tools/deckparse.py` must exist:

1. `$UW_SLIDES_HOME`, if set (`printenv UW_SLIDES_HOME`). Use this to point at a development checkout.
2. The plugin this skill was loaded from, two directories above this `SKILL.md` (`<PLUGIN>/skills/<skill>/SKILL.md`). Take the skill's path from your client, for example Claude Code's "Base directory for this skill", and resolve symlinks. This is where Claude Code, Codex, Copilot and other Agent Plugins clients install the plugin.
3. `~/.claude/plugins/local/uw-slides`, the legacy symlink install.

If none of these has `tools/deckparse.py`, stop and ask the user where the plugin is.

Write every path literally when you run a command. Never use shell variables (`PLUGIN=... python3 $PLUGIN/...`): Claude Code cannot match an allow rule against them, so each run asks for permission.

Run each command exactly as this skill writes it, as one command with nothing appended: no redirects (`2>/dev/null`), no `; echo "exit: $?"`, no `&&`, pipes, loops or leading `cd`. Claude Code checks every part of a compound command, so one part that no rule matches makes the whole command ask. Check whether `UW_SLIDES_HOME` is set by running `printenv UW_SLIDES_HOME` alone (no output means it is not set), and check that a file exists with the Glob or Read tool, not with `ls` or `test` in the shell.

## Brand Resolution

Resolve the brand in this order:
1. `--brand=` flag if provided
2. `.brand` file in the current directory if it exists
3. Default to `uw`

## Usage

```
/uw-slides:generate-slides                 # generate missing slides, ask about stale ones
/uw-slides:generate-slides <id> [<id>...]  # only these slides
```

Run from inside the presentation directory. All `deckparse.py` commands use the vendored copy at `tools/deckparse.py` (put there by `/uw-slides:new-deck`).

**Permissions.** Decks made by a plugin version with `tools/deckperms.py` ship Claude Code allow rules in `.claude/settings.json` for everything this skill runs: `deckparse.py`, `resolve-catalog.py resolve`, the build scripts, and writes to `content/` and `slides/`. The plugin's own files (layouts, brand rules, schemas) are covered by a Read rule in `.claude/settings.local.json`. A deck made earlier has neither: if the user is being asked to approve each command, tell them to run `/uw-slides:update-deck`, which adds the rules. Keep to the literal single-command forms below, or the rules cannot match. Do not ask the user to approve commands one by one when the rules are missing; point them at the update.

## Read first

- `<PLUGIN>/design-systems/<brand>-brand/DESIGN.md`: the brand rules
- `<PLUGIN>/references/layouts.md`: the layout library, slot limits, fill procedure (section 2) and `custom` rules (section 6)
- `<PLUGIN>/references/slide-schema.md`: brief fields, staleness hash, generation rules (section 5)
- `<PLUGIN>/references/accessibility-requirements.md`
- the font-size rules in `<PLUGIN>/CLAUDE.md` (minimum `1.5rem`; `1rem` only for source lines and uppercase labels)

## Procedure

**Start fresh on every invocation.** Briefs, `deck.yml` and `content/` change between runs: the user adds briefs, edits wording and hand-edits HTML. Re-read them from disk every time this skill runs, even if you read them earlier in the same conversation, and never decide what to generate from memory of a previous run. Step 1 gives the current state of every slide.

### 1. Get the state of every slide

```bash
python3 tools/deckparse.py status .
```

It prints one line per slide in `deck.yml` order. Act on the state, never on guesses:

| State | Meaning | Action |
|-------|---------|--------|
| `missing` | no `content/<id>.html` | generate |
| `stale` | the brief changed since the HTML was generated | list these, **ask before overwriting**, then generate the confirmed ones |
| `untracked` | HTML exists without `data-brief-hash` (hand-written or older) | **ask**: overwrite, or keep it by setting `locked: true` in the brief |
| `fresh` | HTML matches the brief | skip |
| `locked` | brief has `locked: true` (hand-edited HTML) | **never write**; report it. To regenerate, the user sets `locked: false` |
| `catalog` | brief has `use: catalog/<id>` | resolve with the catalog resolver (step 2); never generate |
| `no-brief`, `invalid` | `slides/<id>.md` missing or does not parse | skip and report the file and line; the user fixes it |

If the user named slide IDs, restrict to those. If `deck.yml` itself does not parse, stop and show the error. `orphan-brief` and `orphan-fragment` lines are reported, not acted on.

### 2. Resolve catalog slides

Skip this step if no slide is in state `catalog`, or if the user named slide IDs and none is a catalog slide. Otherwise run, from the deck directory:

```bash
python3 tools/resolve-catalog.py resolve . --catalog=<PLUGIN>/catalog
```

Write `<PLUGIN>` as the resolved absolute path (see Plugin directory), so the command stays literal; never save it in a file in the deck. The resolver rewrites `content/<id>.html` for every catalog slide in the deck (it cannot be limited to one), so a catalog slide's HTML is never hand-edited: to customise one, eject it (`python3 tools/resolve-catalog.py eject . <id> --catalog=<PLUGIN>/catalog`), which turns it into a locked layout slide.

Keep the resolver's output for the report. Pass its warnings on exactly as printed, including placeholder warnings (such as the `funding` slide's default agency and grant ID) and brand-mismatch warnings, and name the params the user still has to set. If it exits non-zero (catalog not found, a slide that did not resolve), show the output, list the slides that failed, and carry on with the layout slides; do not stop the run.

### 3. Generate each slide

For every layout slide you are going to write (not the catalog slides):

1. **Read the brief**: `python3 tools/deckparse.py brief slides/<id>.md` (JSON: front matter and body).
2. **Resolve the layout.**
   - A layout ID: it must be a file in `<PLUGIN>/templates/layouts/` (`layouts.md`, section 1). Unknown ID: stop and report.
   - `auto`: choose with `layouts.md`, section 5, **write the chosen ID and a `layout_rationale` back into the brief's front matter**, and only then continue (the hash covers `layout`).
   - `custom`: follow `layout_intent` and the rules in `layouts.md`, section 6.
3. **Check the content fits** the layout's limits (`layouts.md`, section 4). If it does not, report it and propose either shorter text (for the user to approve in the brief) or a different layout. Never shrink fonts or silently cut the brief's text.
4. **Fill the layout** exactly as in `layouts.md`, section 2: copy `<PLUGIN>/templates/layouts/<layout>.html`, rename `layout-<layout>` to the slide ID in `data-slide` and every CSS selector, fill each `data-slot` / `data-param`, remove optional elements the brief leaves empty. Replace every sample list item (never append to the template's `<li>`s) and render Markdown to HTML. Before writing, check the output: the number of list items equals the brief's, none of the template's sample text remains, and no literal `-`, `**` or `1.` is left in a text node. `custom` slides are written from scratch to the same standard (scoped `section[data-slide="<id>"]` styles, brand tokens, one `<h1>`, accent bar).
5. **Apply the generation rules** (`slide-schema.md`, section 5):
   - the key message is the headline and usually the main text shown;
   - talking points are **never** rendered verbatim;
   - **speaker notes**: if the brief has a `## Notes` section, render its content as `<aside class="notes">` as the **last child** of the `<section>` element. This is the only place notes appear; they are never rendered in the main slide view. reveal.js shows them in presenter view (S key); the legacy footer ignores them.
   - the source renders as the small footer line;
   - pass 1 uses no photographs and no decorative icons: it must look finished without images;
   - `aria-label` is `Slide N: <title, else key message>`, where N is the position in `deck.yml`.
6. **Stamp provenance** on the root `<section>`, after any write-back to the brief:
   - `data-layout="<layout id or custom>"`
   - `data-brief-hash="<output of python3 tools/deckparse.py hash slides/<id>.md>"`
   - `data-generated-by="uw-slides@<plugin version>"` (version from `<PLUGIN>/plugin.json`)
7. **Write** `content/<id>.html` (create `content/` if needed).

### 4. Build and report

```bash
./build.sh
./outline.sh        # refreshes OUTLINE.md (read-only overview)
```

Then run `/uw-slides:design-review` and `/uw-slides:accessibility-check`, and report:

```
✓ Generated:   02-why-cloud (bullets), 05-demo (exercise)
↻ Regenerated: 03-costs (stale, confirmed)
⏭ Fresh:       01-title
🔒 Locked:      04-diagram (hand-edited; not touched)
📦 Catalog:     06-intro (catalog/uw-title, resolved)
⚠ Catalog:     08-funding: placeholder agency, grant ID and title still shown (set params in slides/08-funding.md)
⚠ Skipped:     07-recap (slides/07-recap.md:12: unknown field 'colour')
Layout choices written back to briefs: 02-why-cloud (auto -> bullets)
```

## Rules

- **Never overwrite a locked slide, and never overwrite a stale or untracked one without asking.** If the user wants to hand-edit generated HTML, tell them to set `locked: true` in the brief first, or the next run will replace the edit.
- Changing `layout_rationale`, `objective`, `owner`, `status`, `duration`, `locked`, `section` or `## Notes` does not make a slide stale; changing the key message, talking points, source, slots, `title`, `layout`, `layout_intent`, `use` or `params` does.
- Fix problems in the brief or the layout choice, not by hand-tuning one slide's CSS away from the library.
- Never generate a catalog slide or edit its resolved HTML by hand; run the resolver (step 2) or eject the slide.
- Slide fragments only ever touch `content/`. Pass 2 (`apply-visuals`) writes `content-with-visuals/`.
