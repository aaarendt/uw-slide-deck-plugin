# Deck and Slide Brief Schema

Defines the files that describe a deck: `deck.yml` (metadata and order) and
`slides/<id>.md` (one brief per slide). This extends and supersedes
[markdown-schema.md](markdown-schema.md); see [Mapping from older formats](#6-mapping-from-older-formats).

```
<deck>/
├── deck.yml            # deck metadata + ordered slide IDs
├── slides/<id>.md      # one brief per slide: front matter + body
└── content/<id>.html   # generated or catalog-resolved fragments
```

Filename stem = `id` = `data-slide` value. IDs are lowercase letters, digits and
single hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`); they may start with a letter or a
digit (`title`, `03-approach`). Files in `slides/` whose names start with `_`
are templates, not slides.

The parser and validator is `tools/deckparse.py` (Python 3 standard library
only). It is the reference implementation of this document.

## 1. File syntax: the YAML subset

`deck.yml` and brief front matter use a **restricted subset of YAML 1.2**. Every
accepted file is valid YAML, so editors work and PyYAML or ruamel.yaml could
replace the parser later without touching any file. Anything outside the subset
is **rejected with `file:line: message`**, never guessed at.

Supported:

| Construct | Rules |
|-----------|-------|
| Comments | Whole-line only (`# ...`), at any indent. Blank lines are ignored. |
| Keys | `[A-Za-z_][A-Za-z0-9_-]*`, plain (unquoted), followed by `:` and a space or end of line. Must be unique within their map. |
| Strings | Plain (`hello world`), `"double"` (escapes: `\"` and `\\` only) or `'single'` (`''` for a quote). Quote any value that contains `: ` or ` #`, starts with an indicator character, or would otherwise look like a number, date or keyword. |
| Integers | `-?(0\|[1-9][0-9]*)`, e.g. `30`. |
| Booleans | `true` and `false` (lowercase). |
| Null | `null`, `~`, or an empty value (`key:` with nothing nested). |
| Lists | Block lists of scalars: `- item` per line, indented 0 or more spaces under their key. `key: []` is an empty list. |
| Nested map | **One** level: a key whose value is an indented block of `key: scalar` lines. |

Rejected (with an error): anchors/aliases (`&`, `*`), tags (`!`), block scalars
(`|`, `>`), multi-line values (plain, quoted or continuation lines),
flow-style collections (`{...}` and non-empty `[...]`), tabs, duplicate keys,
trailing comments after a value, document markers (`---`, `...`), quoted or
numeric keys, nesting deeper than one level, maps or lists inside lists, and
**ambiguous plain scalars**: `Null/True/False` in other cases, numbers with a
leading `+` or leading zero, floats, hex/octal/binary, sexagesimal (`1:30`) and
dates (`2026-10-09`). Quote those to keep them strings (`"2026-10-09"`, `"007"`).

`yes`, `no`, `on`, `off` are plain strings. (YAML 1.2 loaders agree; the YAML 1.1
loader in PyYAML reads them as booleans, so a future PyYAML switch needs a 1.2
loader or custom resolver. Quote them if a string is intended.)

Files are UTF-8; CRLF line endings and a BOM are tolerated.

## 2. `deck.yml`

Flat deck metadata plus the ordered slide list. Per-slide data never lives here
(it lives in the brief), so reordering is a one-line move.

```yaml
title: "Cloud Basics"
audience: "Graduate students new to cloud computing"
duration: 60
presenter: "Jane Doe"
date: "2026-11-03"
catalog: v1.0.0
objectives:
  obj-1: "Explain what the cloud is"
  obj-2: "Launch a VM"
slides:
  - title
  - 02-what-is-cloud
  - demo
```

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `title` | string | yes | Deck title. |
| `slides` | list of IDs | yes | Build order. Unique IDs; `[]` is allowed for an empty deck. |
| `audience` | string | no | Who the deck is for. |
| `duration` | integer | no | Total talk length in **minutes**. |
| `presenter` | string | no | Presenter name. |
| `date` | string | no | Free text; quote it. |
| `catalog` | string | no | Catalog version pin for `use: catalog/...` slides (format owned by the catalog resolver). |
| `objectives` | map `id: text` | no | Learning objectives; briefs refer to the keys. Keys follow the YAML key rule above. |

Unknown fields are errors (they are almost always typos).

## 3. Slide briefs

A brief is a Markdown file: a front matter block between `---` lines at the very
top, then a body.

```markdown
---
id: why-cloud
layout: stat-callout
objective: obj-1
owner: jdoe
status: review
---

# Key message
Most research compute is idle 70% of the time.

## Talking points
- Idle hardware is paid for either way

## Slot: stat
70%

## Source
Smith et al., 2024

## Notes
Pause after the number.
```

### 3.1 Front matter

Only `id` is required. Defaults apply when a field is omitted.

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `id` | string | — | Slide ID; must equal the file name stem (not enforced for `_*.md` templates). |
| `title` | string | none | Short label for `aria-label`, outlines and navigation. Not the headline (that is the key message). |
| `layout` | string | `auto` | `auto` (planner chooses), `custom` (see `layout_intent`), or a layout ID from the layout library ([layouts.md](layouts.md)). The parser checks the format; the lint checks the ID exists. |
| `layout_rationale` | string | none | Why this layout fits; written by the planner, informational only. |
| `layout_intent` | string | none | Required with `layout: custom`, forbidden otherwise: describes the layout wanted. |
| `objective` | string or list | none | Objective ID(s) from `deck.yml` `objectives:` (the lint checks they exist). |
| `owner` | string | none | Person responsible (name or handle). |
| `status` | `draft` \| `review` \| `done` | `draft` | Workflow state. |
| `duration` | integer | none | Estimated speaking time in **minutes** (round up; use `1` for anything shorter). |
| `locked` | boolean | `false` | `true` = the HTML is hand-edited; generators must not overwrite `content/<id>.html`. |
| `use` | string | none | `catalog/<id>`: copy a finished catalog slide instead of generating. Cannot be combined with `layout` or `layout_intent`. |
| `params` | map of scalars | `{}` | One level of `key: scalar`. For layout slides: layout-specific options (e.g. `background`, `eyebrow`); for catalog slides: the slide's parameters. |
| `section` | string | none | Logical grouping used by outlines. |

Unknown fields are errors. Speaker notes are **not** a front matter field; they
go in `## Notes`.

### 3.2 Body

Headings are only recognized at levels 1 and 2 outside code fences; `###` and
deeper are ordinary content. Each section may appear once, in any order. Text
before the first heading is an error.

| Heading | Required | Content |
|---------|----------|---------|
| `# Key message` | yes, unless `use` is set | The one thing shown large on the slide: a phrase, number or one sentence. |
| `## Talking points` | no | Bullets the speaker says aloud. Never rendered verbatim. |
| `## Slot: <name>` | per layout | Content for a named region of the chosen layout (`<name>` is lowercase letters, digits and hyphens, starting with a letter). Slot names are defined by each layout in the [layout library](layouts.md). |
| `## Source` | no | Citation, rendered as a small footer line. |
| `## Notes` | no | Speaker-only notes. Never rendered on the slide. |

Any other heading (for example `## Speaker notes` or `## Visual notes`) is an
error: rename or remove it. Visual notes belong in `VISUALS.md` (pass 2).

## 4. Staleness hash (`data-brief-hash`)

Generated HTML records the brief it was generated from, for example
`<section data-slide="brief-full" data-layout="stat-callout" data-brief-hash="3df0f304a368" ...>`.
A slide is **stale** when its brief's current hash differs from the one in its
HTML. Compute it with `python3 tools/deckparse.py hash slides/<id>.md`.

Algorithm (v1):

1. Parse the brief and apply defaults (so writing `layout: auto` or an empty
   `params:` explicitly does not change the hash).
2. Build one JSON object with exactly these members (nothing else):
   `id`, `title`, `layout`, `layout_intent`, `use`, `params`, `key_message`,
   `talking_points`, `source`, `slots` (map of slot name → text). Missing values
   are `null`.
3. Normalize every body text: Unicode NFC, trailing whitespace removed from
   each line, runs of blank lines collapsed to one, leading and trailing blank
   lines removed, `\n` line endings. Leading indentation and inner spacing are
   kept (they carry Markdown meaning).
4. Serialize as JSON with sorted keys, separators `,` and `:` (no spaces) and
   non-ASCII characters unescaped; encode as UTF-8.
5. `data-brief-hash` = first 12 hex digits of the SHA-256 of those bytes.

**Not hashed** (changing them never makes a slide stale): `layout_rationale`,
`objective`, `owner`, `status`, `duration`, `locked`, `section`, and
`## Notes`. If a future runtime renders notes into the HTML, notes must be added
to the hash and the algorithm version bumped.

## 5. Generation rules

These rules apply to every deck and are followed by whatever generates
`content/*.html` from briefs (the generation skill, WS5). They are not copied
into each deck.

**Two-pass workflow.** Pass 1 builds content and structure from `deck.yml` and
briefs. Pass 2 (`VISUALS.md`) *adds* photographs, diagrammatic accents and
iconography to already-rendered slides; it never rebuilds them.

- Pass 1 uses only typography, layout, colour palette and the gold accent. **No
  photographs and no decorative icons.** The deck must look finished if it had
  to be presented tomorrow with no images.
- Do not anticipate pass 2. If a slide feels sparse, strengthen typography or
  layout; do not add a placeholder.
- The **key message** is the headline and usually the main text shown, set in
  large type.
- **Talking points** are spoken aloud; never render them verbatim.
- **Notes** are for the speaker only; never render them.
- **Source** renders as a small footer citation
  (`clamp(1rem, 1.1vw, 1.25rem)`), never as a content bullet.
- Default to **one anchoring element** per slide (a phrase, a number or a small
  structural composition). When in doubt, use less text.
- Keep visual continuity: consistent type scale, generous whitespace and the
  gold accent bar.
- Slides are `<section data-slide="<id>">` fragments with styles scoped as
  `section[data-slide="<id>"]`, and follow the font-size rules in `CLAUDE.md`.
- Never overwrite `content/<id>.html` when the brief has `locked: true`.

## 6. Mapping from older formats

### `SLIDES.md` (legacy decks)

| `SLIDES.md` | New schema |
|-------------|-----------|
| `# Title` and intro paragraph | `deck.yml` `title` |
| `Target audience:` / `Duration:` lines | `deck.yml` `audience` / `duration` (minutes) |
| `## <slide-id>` heading | One entry in `deck.yml` `slides:` plus `slides/<slide-id>.md` with `id: <slide-id>`; heading order = list order |
| Key message line | `# Key message` |
| Bullets | `## Talking points` |
| Note to self | `## Notes` |
| Source line | `## Source` |
| Other prose under the heading | `## Talking points` or `## Notes`, whichever it is; ask when unclear |
| "How to render this deck" section | Not migrated; superseded by [Generation rules](#5-generation-rules) |

**Deprecation timeline (decision D11).** `SLIDES.md` is phased out, not kept
alongside `deck.yml` (two sources of truth drift).

1. Builds use `deck.yml` when present and fall back to `SLIDES.md` for legacy decks.
2. New decks scaffold `deck.yml` + `slides/` and no `SLIDES.md`.
3. Migration converts legacy decks using the table above.
4. The fallback prints a deprecation warning in v0.2.0 and is removed in a later
   release (target v0.3.0). A one-page `OUTLINE.md`, if wanted, is generated and
   read-only.

### `markdown-schema.md` front matter

| Old field | New |
|-----------|-----|
| `slide_id` | `id` |
| `title` | `title` (now optional) |
| `layout` | `layout` (values must be [layout-library](layouts.md) IDs; the old names are mapped in its "Old layout names" section) |
| `background` | `params: background` |
| `section` | `section` |
| `duration_min` | `duration` (minutes) |
| `presenter` | `deck.yml` `presenter` |
| `eyebrow` | `params: eyebrow` |
| `accent_bar` | dropped: every slide has the gold bar |
| `alt_texts` | dropped: image descriptions belong to pass 2 (`VISUALS.md`) |
| `## Key message` | `# Key message` |
| `## Talking points` | `## Talking points` |
| `## Visual notes` | dropped: `VISUALS.md` |
| `## Speaker notes` | `## Notes` |

## 7. Tooling

```bash
python3 tools/deckparse.py deck  deck.yml                      # validated JSON
python3 tools/deckparse.py deck  deck.yml --format ids         # one slide ID per line, in order
python3 tools/deckparse.py brief slides/<id>.md                # JSON: front_matter, body, hash
python3 tools/deckparse.py brief slides/<id>.md --format kv    # key=value lines (params.<k>=<v>)
python3 tools/deckparse.py hash  slides/<id>.md                # data-brief-hash value
python3 tools/deckparse.py status  <deck-dir>                  # one line per slide: missing, stale, untracked, fresh, locked, catalog, ...
python3 tools/deckparse.py status  <deck-dir> --format json    # the same, plus orphan briefs and fragments
python3 tools/deckparse.py outline <deck-dir>                  # OUTLINE.md content on stdout (./outline.sh writes the file)
python3 tools/test_deckparse.py                                # run the parser tests
```

`status` compares each brief's hash with the `data-brief-hash` in `content/<id>.html`:

| State | Meaning |
|-------|---------|
| `missing` | no fragment yet |
| `fresh` / `stale` | the fragment's hash equals / differs from the brief's |
| `untracked` | fragment has no `data-brief-hash` (hand-written or older) |
| `locked` | brief has `locked: true`; generators never write it |
| `catalog` | brief has `use:`; copied by the catalog resolver, never generated (takes precedence over `locked`) |
| `no-brief`, `invalid` | `slides/<id>.md` is missing or does not parse (exit status 1) |

`outline` renders a deterministic Markdown table (ID, key message, layout, minutes, owner, status, objectives) with a "generated, do not edit" header, the planned minutes against `deck.yml` `duration`, and objective coverage.

Exit status is 0 on success, 1 on a parse or validation error (message on stderr
as `file:line: message`) and 2 on bad usage (`status` also exits 1 when a slide
is `no-brief` or `invalid`). Further cross-file checks (objective IDs exist,
layout IDs exist, `data-slide` matches the file name) belong to the lint (WS7).
