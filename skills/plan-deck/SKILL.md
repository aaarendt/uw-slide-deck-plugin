---
name: plan-deck
description: Plan a deck from a topic, audience and duration. Drafts learning objectives, chooses a layout for every slide, fills the slots, writes deck.yml and slides/<id>.md briefs, validates them, and stops at an approval gate before any HTML. Also re-plans an existing deck (add, remove, merge, split, change length) while respecting locked, owned and done slides.
---

# Plan Deck

## Purpose

Turn a topic into a reviewable plan: `deck.yml` (metadata, objectives, order) and one brief per slide in `slides/<id>.md`. The planner decides the message, the layout and the slot content of every slide, shows the result as an outline for approval, and **stops**. It never writes HTML: `/uw-slides:generate-slides` does that after the user approves.

```
topic + audience + duration
   │  /uw-slides:plan-deck        (this skill: objectives → slides → briefs → approval gate)
   ▼
deck.yml + slides/*.md            (validated with deckparse.py)
   │  /uw-slides:generate-slides  (separate step, after approval)
   ▼
content/*.html
```

Catalog slides (`use: catalog/<id>`) are supported. Read `catalog/catalog.yml` before planning and choose catalog slides first when they fit (see step 3). Slides that already have `use:` in a re-plan are left as-is (see Re-plan).

## Usage

```
/uw-slides:plan-deck                          # interview for the essentials, then plan
/uw-slides:plan-deck "<topic>" [options]      # plan this topic
/uw-slides:plan-deck replan "<change>"        # change an existing plan (see Re-plan)
```

Options (all optional; ask only for what is missing and essential):

| Option | Meaning |
|--------|---------|
| `--audience="..."` | Who the deck is for |
| `--duration=<minutes>` | Total talk length in minutes |
| `--slides=<n>` | Target number of slides |
| `--sources=<path>[,<path>...]` | Source material to draw facts from (files or folders) |
| `--presenter="..."` | Presenter name (goes in `deck.yml`) |

Run from inside a presentation directory created by `/uw-slides:new-deck` (it must contain `deck.yml` and `slides/`). If there is no `deck.yml`, stop and tell the user to run `/uw-slides:new-deck <name>` first. The brand comes from the `.brand` file; layouts are brand-neutral, so planning does not depend on it.

## Setup

Do this once per invocation, before anything else.

1. Confirm `tools/deckparse.py` exists in the deck directory (put there by `/uw-slides:new-deck`). If it is missing, ask the user to run `/uw-slides:new-deck` first, or copy it from `$UW_SLIDES_HOME/tools/deckparse.py` (default: `~/.claude/plugins/local/uw-slides/tools/deckparse.py`).
2. Every `deckparse.py` command below is a single, literal command of this exact form — no leading `VAR=...` assignment, no `cd`, no `&&` chain, no loop, no `${...}` expansion. Run from the deck directory; the recommended allow rule is `Bash(python3 tools/deckparse.py *)`.
3. Read and write files with the file tools, not shell redirection.

## Read first

Read these from disk on every invocation (never rely on an earlier read in the conversation):

- `references/slide-schema.md`: deck and brief fields, YAML subset, body sections, generation rules
- `references/layouts.md`: catalogue (section 1), per-layout limits and example briefs (section 4), choosing a layout and variety rules (section 5), `custom` rules (section 6)
- `catalog/catalog.yml`: catalog index (if present at `$UW_SLIDES_HOME/catalog/catalog.yml` or the plugin default); read each `catalog/slides/<id>/slide.md` for the slides you are considering to see its params. **Brand filter:** skip any slide whose `brand:` field is neither `any` nor the deck's brand (from the `.brand` file in the deck root; default `uw`).
- the source material the user named, if any
- for a re-plan: `deck.yml`, every `slides/*.md`, and the `status` output (below)

## Procedure

### 1. Gather the inputs

Needed: **topic**, **audience**, **duration** (minutes) or **slide count**. Ask only for what is missing, one question at a time, with choices where possible. Do not ask about anything you can state as an assumption.

- Duration and slide count both given: check they agree with the pacing rules (step 3). If they do not, say so and ask which one wins.
- Only one given: derive the other (about 4 minutes per content slide, plus the title and closing).
- Neither given: ask for the duration.
- Presenter, source material and logo are optional. Never invent a presenter, contact, affiliation or date. A logo goes in `params.logo` only if the user names a file that exists under `assets/images/`; then `params.logo_alt` is required.

Write down the **assumptions** you made (audience level, tone, scope, anything you inferred) and show them at the approval gate.

### 2. Draft and confirm the learning objectives

Propose 2-4 objectives, phrased as what the audience can do or understand afterwards ("Explain...", "Launch...", not "Learn about..."). Use the source material when given. **Ask the user to confirm or edit them** before planning slides. Objective IDs are `obj-1`, `obj-2`, ... (keys of `objectives:` in `deck.yml`).

### 3. Plan the slides

Decide, for each slide, its ID, the message, the objective it serves, its layout and its minutes.

**Pacing.** About 4 minutes per content slide. The title and a section divider take 1 minute each; the closing takes 1-2. An exercise takes as long as the activity needs (5-15 minutes) and counts as a content slide for pacing. When the deck is 20 minutes or longer, place an exercise every 3-4 content slides, a recap near the end (a `bullets` or `key-message` slide restating the objectives) and a call to action in the closing. Brief `duration` values are integer minutes (at least 1) and **their sum must equal the deck duration** (a difference of 1 minute is acceptable when exact is impossible). Adjust exercises first, then content slides.

**Structure.** First slide `title`, last slide `closing`. Open the content with why the topic matters to this audience, end with the recap. Every objective is covered by at least one slide, and every content slide serves an objective (`objective:`; the title, dividers and closing may have none).

**Catalog slides.** Before choosing layouts, check `catalog/catalog.yml` for slides that match a structural role in the deck (title, land acknowledgement, funding, agenda, feedback, closing). Use a catalog slide when:
- the slide's purpose matches the catalog description exactly, AND
- the catalog slide's `status` is `ready`.
Write `use: catalog/<id>` in the brief front matter (no `layout:` — catalog slides bring their own), and fill `params:` from the catalog slide's `slide.md` (omit params you want to use their defaults). `status: draft` catalog slides may be used but flag them in the VERIFY list. Catalog slides that are verbatim (kind: verbatim) need no params; parameterized ones need the params the deck author should supply.

**Layouts.** For non-catalog slides, choose with `references/layouts.md`, section 5, and apply all its variety rules across the whole deck (no more than two identical layouts in a row, `bullets` at most a third of the slides, a number becomes `stat-callout`, audience action becomes `exercise`, dividers only in decks of 8+ slides, at most two `quote`s, `custom` at most one slide in six). Never write `layout: auto`: the planner resolves it. Use `layout: custom` last, only when section 6 allows it, with a one-sentence `layout_intent`. Fill `layout_rationale` for every slide in one short sentence (why this layout fits this message).

**IDs.** Lowercase kebab-case, descriptive, no number prefixes (the order lives in `deck.yml`): `title`, `why-cloud`, `launch-vm`, `closing`. Unique, and equal to the file name.

Check the plan against these rules before writing anything. Fix violations; do not carry them to the gate.

### 4. Fill the slots

For each slide write the real content, not placeholders:

- **Catalog slides** (`use: catalog/<id>`): no `# Key message` or slots — just front matter with `use:` and `params:` (omit params you want defaults for). Write a brief description in `## Notes` so a reviewer knows what the slide shows.
- **`# Key message`** (layout slides): the one thing shown large. It must fit the layout's limit (`layouts.md`, section 4).
- **Required slots** (the layout cannot render without them): `bullets` needs `items`; `two-column` needs `main` and `side`; `comparison` needs `left` and `right` (each with a `###` heading); `stat-callout` needs `stat`; `quote` needs `attribution`; `exercise` needs `time` and `steps`; `code` needs `code`; `diagram` needs `nodes`. Fill the optional slots when they help (`support`, `caption`, `deliverable`, `subtitle`, `action`) and leave them out otherwise. `title` reads `presenter` and `date` from `deck.yml`, so set those there rather than as slots.
- **Slot format**: write each slot exactly as in the example briefs of `layouts.md`, section 4. Lists are plain `- text` lines (`steps` may be `1.`), with no bold, no sub-bullets and one line per item. A `nodes` item is `- Label: short description` on one line, with a label of at most 2 words and a description of at most 6, and 3-4 nodes in total. A `diagram` is a sequence; a mapping or translation between two things ("what you know → the cloud") is a `comparison` (two columns, a heading each) or, for more rows than it holds, `custom`.
- **Respect every limit** in the layout's section: words per heading, items per list, characters in a stat, lines of code. If content does not fit, shorten it or split the slide. Never rely on the generator to cut text.
- **`## Talking points`**: what the speaker says aloud (2-4 bullets), never a copy of the slide text. Slot content is what is shown; talking points are what is said.
- **`## Source`**: only a citation that comes from the provided source material or that you are certain of. Never invent a source. Layouts without a source element (`title`, `section-divider`, `exercise`, `closing`) do not take one.
- **`## Notes`**: speaker-only. Holds the `VERIFY:` lines below.
- **Front matter**: `id`, `title` (short label), `layout`, `layout_rationale`, `objective`, `status: draft`, `duration`, `section` (when the deck has sections), and `owner` only if the user gave one. Leave `locked` out (default `false`).

**Facts and verification.** Prefer facts, numbers, names and quotes from the provided source material. Every factual claim you introduce yourself (a statistic, date, price, quotation, name, or a definition a subject expert could dispute) is marked in that slide's `## Notes` as a line starting `VERIFY:` that states the claim and why it is unverified, for example `VERIFY: 70% idle figure is from general knowledge, not from the provided sources`. A `quote` slide never invents a person or a quotation: use one from the sources, or choose another layout.

### 5. Write the files

Use the file tools.

- **`deck.yml`**: `title`, `audience`, `duration`, `presenter` (when known), `objectives` (`obj-n: "text"`) and `slides:` in order. Quote strings that contain `: `, ` #` or look like numbers or dates. Stay inside the YAML subset (`references/slide-schema.md`, section 1): no trailing comments, no multi-line values. Keep the header comments of the existing file. Do not set `catalog`.
- **`slides/<id>.md`**: one per slide, in the shape of the examples in `layouts.md`, section 4. Fresh plan: replace the scaffold's starter slides (`title`, `example-slide`); delete `slides/example-slide.md` if it is not in the new plan.
- Never write `content/`.

### 6. Validate every file you wrote

Run these, one command per call, from the deck directory:

```bash
python3 tools/deckparse.py deck deck.yml
python3 tools/deckparse.py brief slides/<id>.md
python3 tools/deckparse.py status .
```

Run `brief` once for each brief you wrote or changed. `status` must list every slide as `missing` (fresh plan) or `stale`/`fresh`/`locked`/`catalog`, none as `no-brief` or `invalid`, and no `orphan-brief`. Fix every `file:line: message` error in the file it names and re-run until clean.

Then check what the parser does not (cross-file rules belong to the lint, which does not exist yet, so the planner does them):

1. Every `layout:` is a file in `<plugin>/templates/layouts/`, or `custom` with a `layout_intent`.
2. Every `objective:` is a key of `objectives:` in `deck.yml`, and every objective is used by at least one slide.
3. Minutes add up to the deck duration (`deckparse.py outline .` states planned minutes against the target).
4. The variety rules of `layouts.md`, section 5, hold.
5. Slot limits: for every slide count the key-message words, list items, words per item and characters in `stat` against its layout's limits (`layouts.md`, section 4), and check that every `nodes` item has the form `Label: description`. Fix any slide over a limit before the gate.

### 7. Approval gate

Show, and then **stop**:

1. The assumptions and the objectives.
2. The outline, from `python3 tools/deckparse.py outline .`: print its table (ID, key message, layout, minutes, owner, status, objectives), the planned-minutes line and the objective coverage.
3. For each slide, the filled slot content next to its layout (`stat`, `items`, `steps`, ...): one line or a short list per slide. Talking points and notes stay in the briefs.
4. The `VERIFY:` list: every claim a subject expert should check, with its slide ID.
5. Any slide you could not make fit a limit, and any decision you want the user to take.

Then ask the user (with the ask-user tool when available) to **approve**, **request changes** (redo steps 3-6 for the affected slides, then show the gate again) or **stop here**. If the user edits `deck.yml` or the briefs by hand and then approves, run `deck`, `brief` (for the edited briefs) and `status` again first, so hand edits are validated.

**Until the user approves, write no HTML, run no build and do not call `/uw-slides:generate-slides`.** `content/` and `build/` stay as they are. After approval:

- Run `./outline.sh` to refresh the generated `OUTLINE.md` (read-only; never edit it).
- Leave `status: draft` on every brief (`review` and `done` are for the people working on the slides).
- Tell the user the next steps:
  1. If the deck has catalog slides: `python3 tools/resolve-catalog.py resolve .` (copies catalog fragments to `content/`)
  2. `/uw-slides:generate-slides` (generates layout slides; skips catalog ones)
  3. `./build.sh`
  Do not run them.

## Re-plan

Used when `deck.yml` already holds a plan the user wants to change: `replan "<change>"`, or any request to add, remove, merge, split or reorder slides, or to change the duration or slide count. Run Setup and "Read first", then:

1. **Get the current state**: `deck deck.yml`, `status .` and every brief. A starter scaffold (slides `title` and `example-slide` unchanged) is a fresh plan, not a re-plan.
2. **Classify the slides**:

   | Slide | Rule |
   |-------|------|
   | `locked: true` | Its HTML is hand-edited. Never change its brief content, layout or ID; never remove, merge or split it. It may be moved. |
   | `status: done` | Finished. Content, layout and ID are fixed; removing, merging or splitting it needs the user's explicit confirmation naming the slide. |
   | `owner:` set | Someone else's slide unless the user says they are that person. Changing or removing it needs explicit confirmation naming the slide and its owner. |
   | `use:` set | A catalog slide. Leave its `use:`, `params:` and `id` as-is; it may be moved. To replace it with a different catalog slide or a layout slide, first eject it (`python3 tools/resolve-catalog.py eject . <id>`) and then edit it. |
   | otherwise | Free to change. |

   `status: review` slides are free, but list them in the summary because someone is reviewing them.
3. **Plan the change** with the rules of steps 3-4, treating protected slides as fixed points. Re-check pacing, variety rules, objective coverage and the minutes total for the **whole deck**, not only the changed slides. If protected slides make that impossible (for example the minutes cannot reach the new duration), say exactly why and propose options instead of editing them.
4. **Operations**:
   - **Add**: a new brief and a new `slides:` line at the right position.
   - **Remove**: take the ID out of `deck.yml`, delete `slides/<id>.md` and `content/<id>.html` (only after the user confirmed; never a protected slide). No objective may lose its only slide.
   - **Merge**: keep the first slide's ID, combine message and slots within the layout limits (choose a new layout if needed), remove the others as above.
   - **Split**: keep the original ID for the first part, add new IDs after it, share the minutes.
   - **Reorder**: move lines in `deck.yml`; briefs do not change.
   - **Change duration or count**: rescale minutes, then add, merge or remove free slides; never shrink a protected slide's minutes.
   - Never rename an ID silently (it orphans the fragment). Renaming is remove + add.
5. **Confirm before writing** whenever the change removes, merges or splits slides or touches a protected slide: show a short change table (operation, slide ID, reason, owner/state) and wait. A change that only adds slides or edits free slides can be written straight away.
6. **Write and validate** as in steps 5-6, then run the **approval gate** (step 7). In the gate, add a "what changed" table and list the slides that became `stale` (HTML no longer matches the brief), noting that locked slides are not regenerated. The `VERIFY:` list covers only new or changed claims.

## Rules

- No HTML, no build, no `generate-slides` call before the approval gate is passed; this skill never generates HTML.
- Never edit `content/`, except deleting the fragment of a removed slide as in Re-plan.
- Never invent a source, presenter, contact, date or quotation. Mark LLM-introduced facts `VERIFY:` in the slide's notes.
- Respect `locked`, `status: done`, `owner` and `use`.
- Briefs are the source of truth; `OUTLINE.md` is generated and never hand-edited.
- Every `deckparse.py` call is one command with a literal path (see Setup).
