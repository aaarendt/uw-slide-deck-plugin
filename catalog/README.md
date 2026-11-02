# Slide Catalog

Vetted, reusable slides that any deck can reference by ID. A slide in the catalog is ready to use. The catalog keeps framing slides (title, agenda, funding, feedback, closing) and program introductions consistent across trainings without copying HTML between decks.

For curation rules — how to add, review and version catalog slides — see [CURATION.md](CURATION.md).

---

## How to use a catalog slide

In a slide brief, set `use: catalog/<id>` instead of `layout:`. Add `params:` for any fields you want to fill:

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

The catalog resolver copies the slide's HTML into `content/<deck-id>.html`, rewrites its ID and CSS selectors to match your deck, and substitutes your params. `/uw-slides:generate-slides` runs it for you. To run it by hand, from inside the deck directory, point it at the plugin's catalog:

```bash
python3 tools/resolve-catalog.py resolve . --catalog=<plugin>/catalog
```

`/uw-slides:generate-slides` never generates slides with `use: catalog/...`; it resolves them with this command and reports the resolver's warnings.

`<plugin>` is the directory where the uw-slides plugin is installed. The skills find it for you. When you run the resolver by hand, `--catalog` is usually unnecessary: the deck's `.uw-slides.json` records the plugin location (`plugin_dir`, written by new-deck and refreshed by update-deck). If the plugin has been updated since, run `/uw-slides:update-deck`, pass the path (your agent can tell you where the plugin is installed), or clone this repository and set `UW_SLIDES_HOME` to the clone, in which case you can leave out `--catalog`. Don't save a path from a client's plugin cache in scripts or notes: it can change when the plugin is updated.

### Ejecting a catalog slide

To customise a catalog slide beyond its params, eject it — this copies the resolved HTML into the deck as a locked slide and removes the `use:` reference:

```bash
python3 tools/resolve-catalog.py eject . <slide-id> --catalog=<plugin>/catalog
```

After ejecting, edit `content/<id>.html` directly and set `locked: true` in the brief.

---

## Available slides

### `uw-title` — Title slide
**Kind:** parameterized · **Brand:** uw

Standard opening slide: dark purple background, gold accent bar, title and subtitle centre, presenter details below.

| Param | Required | Default |
|-------|----------|---------|
| `title` | yes | `"Presentation Title"` |
| `subtitle` | no | hidden when empty |
| `presenter` | no | `""` |
| `affiliation` | no | `"University of Washington"` |
| `date` | no | hidden when empty |

```markdown
---
id: title
use: catalog/uw-title
params:
  title: "Cloud Computing for Researchers"
  subtitle: "Introduction and Hands-on Lab"
  presenter: "Jane Doe"
  date: "November 3, 2026"
---
```

---

### `funding` — Funding credit
**Kind:** parameterized · **Brand:** uw

> **Default param values are placeholders.** Set `agency`, `grant-id` and `grant-title` in the brief; the resolver warns while a `PLACEHOLDER` value still shows. Use the exact language required by the award, including the disclaimer. Consult the UW Office of Sponsored Programs (OSP) if unsure.

| Param | Required | Notes |
|-------|----------|-------|
| `agency` | yes | e.g. `"National Science Foundation"` |
| `grant-id` | yes | Award number |
| `grant-title` | no | Project title |
| `disclaimer` | no | Use award-specific language; do not rely on the default |

```markdown
---
id: funding
use: catalog/funding
params:
  agency: "National Science Foundation"
  grant-id: "OAC-1234567"
  grant-title: "CloudBank: Enabling Research and Education in the Public Cloud"
---
```

---

### `agenda` — Agenda
**Kind:** derived · **Brand:** any

Auto-generated from `deck.yml`, in deck order, with minutes where briefs set `duration:`. Slides that share a `section:` become one item named after the section (or, without sections, each `section-divider` and the slides after it). Title and closing slides, hidden slides (`section: hidden`) and the framing catalog slides are left out. Up to 7 items fit in one column and 12 in two; past that the resolver warns. Re-run the resolver after changing titles, sections or durations.

| Param | Required | Default |
|-------|----------|---------|
| `heading` | no | `"Agenda"` |

```markdown
---
id: agenda
use: catalog/agenda
---
```

---

### `feedback` — Session feedback
**Kind:** parameterized · **Brand:** any

Prompts participants to complete a survey. The link is hidden when `url` is empty.

| Param | Required | Default |
|-------|----------|---------|
| `url` | no | hidden when empty |
| `url-label` | no | `"feedback survey"` |
| `heading` | no | `"Share Your Feedback"` |
| `prompt` | no | standard text |

```markdown
---
id: feedback
use: catalog/feedback
params:
  url: "https://forms.example.edu/workshop-feedback"
  url-label: "workshop feedback form"
---
```

---

### `thank-you` — Closing / thank you
**Kind:** parameterized · **Brand:** any

Closing slide with a large message and optional contact details. All fields except `message` are hidden when empty.

| Param | Required | Default |
|-------|----------|---------|
| `message` | no | `"Thank You"` |
| `action` | no | hidden when empty |
| `presenter` | no | `""` |
| `email` | no | `""` |
| `url` | no | `""` |

```markdown
---
id: thank-you
use: catalog/thank-you
params:
  message: "Thank You"
  action: "Launch one VM this week."
  presenter: "Jane Doe"
  email: "jdoe@uw.edu"
  url: "cloudbank.org/resources"
---
```

---

### `cb-title` — CloudBank title slide
**Kind:** parameterized · **Brand:** cloudbank

The CloudBank counterpart of `uw-title`: dark navy background, blue accent bar, title and subtitle centre, presenter details below.

| Param | Required | Default |
|-------|----------|---------|
| `title` | yes | `"Presentation Title"` |
| `subtitle` | no | hidden when empty |
| `presenter` | no | `""` |
| `affiliation` | no | `"CloudBank"` |
| `date` | no | hidden when empty |

```markdown
---
id: title
use: catalog/cb-title
params:
  title: "CloudBank for Researchers"
  subtitle: "Cloud access for NSF-funded research"
  presenter: "Jane Doe"
  date: "November 3, 2026"
---
```

---

### `cb-why-cloud` — Why cloud?
**Kind:** parameterized · **Brand:** cloudbank

General motivation for cloud computing in research, to place before the CloudBank program slides. Six headed items with original line icons (inline SVG): bring compute to the data, scale up on demand, run in parallel, use and deploy LLMs, share reproducible environments, host research services. Example services are named in the speaker notes only.

| Param | Required | Default |
|-------|----------|---------|
| `lead` | no | hidden when empty |

```markdown
---
id: why-cloud
use: catalog/cb-why-cloud
params:
  lead: "The work you're doing this week may benefit from cloud computing. With cloud you can:"
---
```

---

### `cb-what-weve-heard` — What we've heard from researchers
**Kind:** verbatim · **Brand:** cloudbank

A dark "The friction" slide: four paraphrased researcher quotes in cards (no account without a credit card, a 40-hour laptop run, setup different on every platform, a surprise $12K bill), with a source line saying they are paraphrased. Place it between `cb-why-cloud` and `cb-what-is`; each quote is answered by a later CloudBank slide. No params; eject to use your own quotes.

```markdown
---
id: what-weve-heard
use: catalog/cb-what-weve-heard
---
```

---

### `cb-eligibility` — CloudBank eligibility and recommended uses
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against the ACCESS allocations policy and CloudBank's request-access page whenever either changes. The slide's `slide.md` lists its sources.

Who can lead a project and what CloudBank is for: a who/what criteria strip, then "Good fit" and "Better elsewhere" columns. The full original wording of both sources is in the speaker notes. No params; eject to customise.

```markdown
---
id: eligibility
use: catalog/cb-eligibility
---
```

---

### `cb-what-is` — CloudBank overview
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against CloudBank's current pages when they change. The slide's `slide.md` lists its sources.

Four cards: origin, cloud providers, the 2025 CloudBank 2.0 award, and the NAIRR interface role. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: what-is
use: catalog/cb-what-is
---
```

---

### `cb-programs` — CloudBank programs
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against CloudBank's current pages when they change. The slide's `slide.md` lists its sources.

Six short headed items with original line icons (inline SVG): no cost, consulting and helpdesk, account management, multiple clouds, monitoring and optimization, training. No logos. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: programs
use: catalog/cb-programs
---
```

---

### `cb-why-choose` — Why choose CloudBank for an account
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against CloudBank's current pages when they change. The slide's `slide.md` lists its sources.

Three reasons (no card or purchase agreement, one bill for several clouds, cost monitoring and spending cap) and a callout that awards are grant dollars, not credits. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: why-choose
use: catalog/cb-why-choose
---
```

---

### `cb-award-tiers` — Grant award tiers
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against CloudBank's current pages when they change. The slide's `slide.md` lists its sources.

A table of Explore, Discover and Accelerate with range, average and typical use, plus three facts. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: award-tiers
use: catalog/cb-award-tiers
---
```

---

### `cb-process` — Application-to-account process
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against CloudBank's current pages when they change. The slide's `slide.md` lists its sources.

A left-to-right flow of four numbered, described steps ending in a "Start working in the cloud" card, with a text tag under each (ACCESS, CloudBank, Cloud provider) showing which system it happens in. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: process
use: catalog/cb-process
---
```

---

## Adding new catalog slides

See [CURATION.md](CURATION.md) for the full process. In brief:

1. Create `catalog/slides/<id>/` with `slide.html` and `slide.md`.
2. Add an entry to `catalog/catalog.yml`.
3. Open a PR. The slide owner approves the wording before it is merged; a slide in the catalog is ready to use.
