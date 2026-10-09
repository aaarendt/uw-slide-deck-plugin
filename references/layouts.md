# Layout Library

The closed set of slide layouts a brief can name in `layout:` (see
[slide-schema.md](slide-schema.md)). The planner picks from this list; the
generator fills a layout's slots from the brief. Fragments live in
`templates/layouts/<id>.html`; the file name is the layout ID.

All layouts are brand-neutral: they use only the `--slide-*` tokens, so the same
fragment renders in UW and CloudBank decks. Each follows the rules in
`CLAUDE.md` (minimum `1.5rem` text, `1rem` only for source lines and uppercase
labels), has a top or left accent bar and is scoped to
`section[data-slide="<id>"]`.

## 1. Catalogue

| ID | Purpose | Default background | Slots (besides `# Key message`) | Params |
|----|---------|--------------------|---------------------------------|--------|
| `title` | Opening slide | dark | `subtitle`, `presenter`, `affiliation`, `date` | `logo`, `logo_alt` |
| `section-divider` | Break between major sections | deep | `subtitle` | `eyebrow` |
| `key-message` | One sentence the audience must keep | dark | `support`, `source` | `background` |
| `bullets` | A short list of parallel phrases | light | `items`, `source` | `background` |
| `two-column` | Main point plus a supporting aside | light | `main`, `side`, `source` | |
| `comparison` | Two options side by side | light | `left`, `right`, `source` | |
| `stat-callout` | One number that carries the message | light | `stat`, `source` | `background` |
| `quote` | A testimonial or cited statement | subtle | `attribution`, `role`, `source` | `background` |
| `exercise` | Hands-on activity | light | `time`, `steps`, `deliverable` | |
| `code` | Code or terminal commands | light | `code`, `caption`, `source` | |
| `diagram` | A 3-4 step process or flow | light | `nodes`, `caption`, `source` | |
| `closing` | Final slide | dark | `action`, `contact` | `logo`, `logo_alt` |

`# Key message` is always the slide's `<h1>` (the headline). Talking points and
notes are never rendered.

## 2. Filling a layout (generator rules)

1. Copy `templates/layouts/<id>.html` to `content/<slide-id>.html` and replace
   every `layout-<id>` with the slide ID (in `data-slide` and in all CSS
   selectors). Set `aria-label` to `Slide N: <title or key message>`.
2. Replace the sample text of each element marked `data-slot="<name>"` with the
   brief's content for that slot. The key message fills `data-slot="key-message"`.
3. Elements marked `data-optional` are removed when the brief has no content for
   them. `data-param` elements are filled from `params:` and removed when the
   param is absent. Keeping the `data-slot`, `data-optional` and `data-param`
   attributes in the output is harmless and helps tooling.
4. `## Source` fills the `source` slot. Layouts without a `source` element
   (`title`, `section-divider`, `exercise`, `closing`) do not show sources: use
   a layout that does, or put the citation on the previous slide.
5. Add the provenance attributes to `<section>`: `data-layout` (already
   present), `data-brief-hash` and `data-generated-by` (see slide-schema.md §4).
6. Never change the CSS custom properties or structure to fit more text. If
   content exceeds the limits below, shorten it or split the slide.

**Slot content to HTML.** Slot text is Markdown limited to plain text,
`**bold**` (`<strong>`, 1-2 uses per slide at most) and lists.

| Slot | Brief content | HTML |
|------|---------------|------|
| `items` | `-` list | `<li>` per item |
| `steps` | `1.` or `-` list | `<li>` per step (numbers come from CSS) |
| `nodes` | `-` list, each `Label: short description` (description optional) | `<li><span class="label">..</span><span class="desc">..</span></li>` |
| `main`, `side`, `left`, `right` | optional leading `### Heading`, then a paragraph or a `-` list | heading becomes `<h2>`; list becomes `<ul>` |
| `code` | one fenced block | `<pre><code>` with the text HTML-escaped; no syntax highlighting |
| `contact` | one line per contact | `<p>` per line (do not make links) |
| others | one line of text | text content |

`title` also reads `presenter` and `date` from `deck.yml` when the slots are
absent. `params.logo` is a path relative to the deck root; the `<img src>`
is that path prefixed with `../` (the build output is in `build/`).
`params.logo_alt` is required whenever `params.logo` is set.

## 3. Tokens

Every brand header (`design-systems/<brand>/shared/header.html`) defines these
names. A new brand must define all of them.

| Token | UW | CloudBank | Use |
|-------|----|-----------|-----|
| `--slide-bg-dark` | Spirit Purple | Deep Navy | Dark slide background |
| `--slide-bg-deep` | Husky Purple | Ink | Deepest background (dividers, code panel) |
| `--slide-bg-light` | White | White | Light slide background |
| `--slide-bg-subtle` | Husky Gold Web | Fog | Panels and alternate light background |
| `--slide-heading` | Spirit Purple | Deep Navy | Headings on light |
| `--slide-text` | Gray 90 | Ink | Body text on light |
| `--slide-text-muted` | Gray 70 | Gray 70 | Secondary text on light |
| `--slide-text-on-dark` | White | White | Text and headings on dark |
| `--slide-text-muted-on-dark` | Husky Gold Web | Mist | Secondary text on dark |
| `--slide-accent` | Spirit Gold | Signal Blue | Bars, bullets, rules (decorative) |
| `--slide-accent-size` | 8px | 4px | Accent bar thickness |
| `--slide-heading-transform` | uppercase | none | Short headings (not sentences) |
| `--slide-heading-weight` | 800 | 800 | Heading weight |

Never use the accent for text. Signal Blue on Deep Navy is 2.3:1 and fails
contrast: it is acceptable only for the decorative bars, bullets and rules the
layouts already use.

**Background variants.** Each fragment defines four local variables on its
`<section>`: `--bg`, `--fg`, `--fg-muted`, `--head`. `params: background` swaps
them, on the layouts that list it in the catalogue only. For `dark`:
`--bg: var(--slide-bg-dark); --fg: var(--slide-text-on-dark);
--fg-muted: var(--slide-text-muted-on-dark); --head: var(--slide-text-on-dark);`
For `light`: `--bg: var(--slide-bg-light); --fg: var(--slide-text);
--fg-muted: var(--slide-text-muted); --head: var(--slide-heading);`.

## 4. Layouts

Limits are per slide; words are counted in the shown text. They are tested to
fit at 16:9 and 4:3 (see §7).

### `title`
Opening slide: deck title, subtitle, presenter. Centered, dark, logo on top.
- **Use when:** first slide of every deck.
- **Avoid when:** anywhere else (use `section-divider` or `closing`).
- **Limits:** key message ≤ 10 words; subtitle ≤ 14; logo optional.

```markdown
---
id: title
layout: title
params:
  logo: assets/images/logo.png
  logo_alt: "University of Washington"
---
# Key message
Cloud Basics for Researchers

## Slot: subtitle
Run your first analysis in the cloud
```

### `section-divider`
Full-bleed marker between sections, left aligned on the deepest background.
- **Use when:** a deck has 8+ slides and a clear change of topic.
- **Avoid when:** two in a row; a section of one or two slides.
- **Limits:** key message ≤ 8 words; subtitle ≤ 14; `params.eyebrow` ≤ 3 words.

```markdown
---
id: part-2
layout: section-divider
params:
  eyebrow: "Part 2"
---
# Key message
Launching your first virtual machine
```

### `key-message`
One large sentence. The default "say one thing" slide.
- **Use when:** the point is a claim, not a list; to reset attention.
- **Avoid when:** the claim is mostly a number (`stat-callout`); more than one idea.
- **Limits:** key message ≤ 20 words; `support` ≤ 20 words.

```markdown
---
id: idle-compute
layout: key-message
---
# Key message
Most research compute sits idle, and you still pay for it.

## Slot: support
The cloud bills by the hour, not by the machine.
```

### `bullets`
Heading plus 3-5 short parallel phrases.
- **Use when:** a small set of parallel items (steps, criteria, costs).
- **Avoid when:** items need explanation (put it in talking points), more than
  five items (split the slide), or the list is the whole talk.
- **Limits:** heading ≤ 8 words; 3-5 items, each ≤ 8 words and one line when
  possible. Items are not the talking points.

```markdown
---
id: cost-watch
layout: bullets
---
# Key message
Three costs to watch

## Slot: items
- Compute hours left running
- Data leaving the region
- Storage nobody cleans up
```

### `two-column`
Heading, a main column (about 60%) and a supporting aside in a tinted panel.
- **Use when:** a narrative with one caveat, definition or example attached.
- **Avoid when:** the two sides are equals (`comparison`).
- **Limits:** heading ≤ 8 words; `main` ≤ 4 items of ≤ 10 words, or one paragraph
  of ≤ 40 words; `side` heading ≤ 3 words and ≤ 25 words.

```markdown
---
id: why-cloud
layout: two-column
---
# Key message
Why researchers move to the cloud

## Slot: main
- Capacity on demand for peak workloads
- Pay only for the hours you use

## Slot: side
### Watch out
Idle resources keep billing until you stop them.
```

### `comparison`
Two equal columns split by an accent rule, each with a required heading.
- **Use when:** before/after, option A/B, myth/fact.
- **Avoid when:** more than two options (use `bullets` or two slides); one side
  is much longer than the other.
- **Limits:** heading ≤ 8 words; each column: `###` heading ≤ 3 words and ≤ 4
  items of ≤ 5 words.

```markdown
---
id: laptop-vs-cloud
layout: comparison
---
# Key message
Laptop versus cloud

## Slot: left
### Laptop
- Fixed capacity
- Hard to share

## Slot: right
### Cloud
- Scales to the job
- Shared by default
```

### `stat-callout`
A very large number with a one-line statement.
- **Use when:** the message is a figure (percent, count, cost, duration).
- **Avoid when:** more than one number (use `bullets` or `comparison`); a
  figure without a clear takeaway.
- **Limits:** `stat` ≤ 6 characters (`70%`, `$1.2M`, `3.5×`); key message ≤ 15
  words, phrased so it completes the number ("of research compute sits idle").

```markdown
---
id: idle-share
layout: stat-callout
---
# Key message
of research compute capacity sits idle

## Slot: stat
70%

## Source
Smith et al., 2024
```

### `quote`
A statement attributed to a person, on a tinted background.
- **Use when:** a testimonial, a user need or a cited expert statement.
- **Avoid when:** you are paraphrasing (use `key-message`); more than two per deck.
- **Limits:** key message (the quote, with quotation marks) ≤ 30 words;
  `attribution` ≤ 6 words (required); `role` ≤ 8 words.

```markdown
---
id: core-director
layout: quote
---
# Key message
“The cloud did not make our science faster. It made waiting optional.”

## Slot: attribution
Dr. Maria Chen

## Slot: role
Director, Genomics Core
```

### `exercise`
A hands-on activity: duration chip, title, numbered steps, optional deliverable.
- **Use when:** the audience does something (the planner places one every 3-4
  content slides).
- **Avoid when:** the slide only explains; the task has more than four steps.
- **Limits:** key message ≤ 8 words; `time` ≤ 8 characters (`10 min`); 2-4
  steps of ≤ 10 words; `deliverable` ≤ 10 words.

```markdown
---
id: launch-vm
layout: exercise
---
# Key message
Launch your first virtual machine

## Slot: time
10 min

## Slot: steps
1. Open the console and choose a small instance
2. Connect with the browser terminal
3. Run the test script and note the runtime

## Slot: deliverable
The runtime, pasted in the shared notes
```

### `code`
Heading and a dark code panel.
- **Use when:** the audience reads or types a command or snippet.
- **Avoid when:** the code is longer than the limit (show the key lines and link
  the rest in notes).
- **Limits:** heading ≤ 8 words; code ≤ 6 lines of ≤ 47 characters; `caption` ≤
  15 words. No syntax highlighting in pass 1.

````markdown
---
id: start-vm
layout: code
---
# Key message
Start a VM from the terminal

## Slot: code
```bash
aws ec2 run-instances \
  --instance-type t3.small
```

## Slot: caption
Replace the image ID with the one from the course notes.
````

### `diagram`
A flow of 3-4 boxes joined by chevrons (stacked on 4:3 and narrower).
- **Use when:** a short process, pipeline or architecture in sequence.
- **Avoid when:** branches, loops or more than four nodes: use `layout: custom`
  or a pass-2 diagram (`VISUALS.md`).
- **Limits:** heading ≤ 8 words; 3-4 nodes, label ≤ 2 words, description ≤ 6
  words; `caption` ≤ 15 words.

```markdown
---
id: job-flow
layout: diagram
---
# Key message
How a job runs in the cloud

## Slot: nodes
- Upload: Data to storage
- Launch: Start a VM
- Compute: Run the job
- Retrieve: Download results
```

### `closing`
Final slide: call to action and contact details. Centered, dark, logo on top.
- **Use when:** last slide of every deck.
- **Limits:** key message ≤ 8 words; `action` ≤ 20 words; `contact` ≤ 3 lines.

```markdown
---
id: closing
layout: closing
params:
  logo: assets/images/logo.png
  logo_alt: "University of Washington"
---
# Key message
Questions and next steps

## Slot: action
Launch one VM this week and share what you learn.

## Slot: contact
jane.doe@example.edu
```

## 5. Choosing a layout (planner)

| The slide's message is... | Layout |
|---------------------------|--------|
| the deck title / the last word | `title` / `closing` |
| a change of topic | `section-divider` |
| a claim in one sentence | `key-message` |
| a number | `stat-callout` |
| a short set of parallel items | `bullets` |
| a point with one caveat or definition | `two-column` |
| A versus B | `comparison` |
| something a person said | `quote` |
| something the audience does | `exercise` |
| a command or snippet | `code` |
| a sequence of steps or components | `diagram` |
| none of the above | `custom` (§6) |

**Variety rules.** The planner applies these across the whole deck:

1. No more than two consecutive slides with the same layout. Never two
   `section-divider`s in a row.
2. `bullets` is at most one third of the slides. After three text-led slides in
   a row (`bullets`, `two-column`, `comparison`), use `key-message`,
   `stat-callout`, `quote` or `diagram`.
3. A stat-like message uses `stat-callout`, not a bullet containing a number.
4. First slide `title`, last slide `closing`. Use `section-divider` only in
   decks of eight or more slides, one per section of three or more slides.
5. At most two `quote` slides and use `code` only where the audience reads or
   types code.
6. Any slide where the audience acts is an `exercise`.
7. `custom` is at most one slide in six.

## 6. `layout: custom`

`layout: custom` requires `layout_intent` (the schema rejects it otherwise) and
is the escape hatch, not a style choice.

**Acceptable** when the content has a structure no layout offers (a table, a
timeline, a branching diagram, a dashboard or annotated screenshot) and the
intent can be stated in one sentence.

**Not acceptable** to avoid choosing, to add decoration, to fit more text (cut
text or split the slide) or when two layouts in sequence would work.

A custom slide is generated like any other (scoped styles, tokens only, font
rules, one `<h1>`, accent bar) and is still checked by the reviews and lint.
When the same intent recurs across decks, propose a new layout here.

`layout: auto` is resolved by the planner to a layout ID (or `custom`) before
generation, and the choice is written back to the brief with a
`layout_rationale`.

## 7. Responsive behaviour and verification

Slides fill the viewport (`100vw × 100vh`) and size with `clamp()`, so a layout
scales from 1024 px wide upward. Type never drops below `1.5rem` (labels and
source lines `1rem`). `diagram` stacks below a 3:2 aspect ratio, and the
accent bar, margins and gaps scale with the viewport.

Verified for every layout, in both brands, at 1920×1080 and 1280×720 (16:9)
and 1024×768 and 1600×1200 (4:3), at the maximum content in §4 and with the
sample text: no text below the minimum size, no text outside the slide or
overlapping other text, WCAG AA contrast for all text, brand fonts loaded.

## 8. Old layout names

`references/markdown-schema.md` named these layouts. Map them when migrating:

| Old | New |
|-----|-----|
| `title` | `title` |
| `two-column` | `two-column` (unequal) or `comparison` (equal sides) |
| `comparison` | `comparison` |
| `code` | `code` |
| `transition` | `section-divider` |
| `architecture` | `diagram` (4 nodes or fewer), otherwise `custom` |
| `image-bottom` | no pass-1 equivalent: use the layout for the text and add the image in pass 2 (`VISUALS.md`) |
