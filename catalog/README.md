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

The CloudBank counterpart of `uw-title`, with the logos and award credit NSF requires: the CloudBank and NSF logos with "NSF Awards: 1925001 & 2505560" at the top, title and subtitle centre, presenter details below, and a Deep Navy band of partner logos (SDSC, UC San Diego, University of Washington, UC Berkeley, Strategic Blue) along the bottom. The logos and award line are fixed; they ship in the slide's `assets/` folder and are copied into the deck when it resolves.

| Param | Required | Default |
|-------|----------|---------|
| `title` | yes | `"Presentation Title"` |
| `subtitle` | no | hidden when empty |
| `presenter` | no | `""` |
| `affiliation` | no | hidden when empty |
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
  lead: "Commercial cloud computing can help with research like yours. With cloud you can:"
---
```

---

### `cb-what-weve-heard` — What we've heard from researchers
**Kind:** verbatim · **Brand:** cloudbank

A dark "The friction" slide: four paraphrased researcher quotes in cards (no account without a credit card, no time to learn it all, setup different on every platform, an opaque $12K bill), with a source line saying they are paraphrased. Place it between `cb-why-cloud` and `cb-what-is`; each quote is answered by a later CloudBank slide. No params; eject to use your own quotes.

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

### `cb-research-and-classroom` — Two ways to use CloudBank
**Kind:** verbatim · **Brand:** cloudbank

CloudBank Research and CloudBank Classroom side by side: a table with each offering's logo as a column header and rows for who it is for, what you get and how to start. Place it right after `cb-what-is`. No params; eject to customise.

```markdown
---
id: research-and-classroom
use: catalog/cb-research-and-classroom
---
```

---

### `cb-why-choose` — What you get with a CloudBank account
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against CloudBank's current pages when they change. The slide's `slide.md` lists its sources.

Two columns of four headed items with original line icons. "Billing, handled for you": no credit card, one bill across several clouds, a spending cap, dollars rather than credits. "Accounts, handled for you": set up after onboarding, one login to each cloud, collaborators managed in one place, another cloud added later. Version 2.0.0 merged the former `cb-programs` slide into this one. No params; eject to customise.

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

### `cb-nairr` — CloudBank through the NAIRR Pilot
**Kind:** verbatim · **Brand:** cloudbank

> **Program policy wording.** Re-check against the NAIRR Pilot pages whenever they change, and when NAIRR moves from the pilot to the NAIRR Operations Center. The slide's `slide.md` lists its sources.

The second route to a CloudBank account: four differences from ACCESS (AI focus, everyone on the project U.S.-based, cash awards, longer review) and three numbered steps to request it (prepare, request, onboard), with a pointer to NAIRR Classroom projects for educators. The full wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: nairr
use: catalog/cb-nairr
---
```

---

### `cb-by-the-numbers` — CloudBank by the numbers
**Kind:** parameterized · **Brand:** cloudbank

> **Program figures.** The defaults are the October 2026 figures. Update them and bump the slide's `version` when new figures are published; a deck can set newer ones in its brief meanwhile.

Three headline stats (research projects awarded, dollars allocated to research, CloudBank Classroom courses), research awards by tier with average award, and the top three research fields with a count of the rest. Every figure is a param.

```markdown
---
id: by-the-numbers
use: catalog/cb-by-the-numbers
params:
  period: "October 2025 to October 2026"
---
```

---

### `cb-rule-of-thumb-costs` — Rule-of-thumb cloud costs
**Kind:** verbatim · **Brand:** cloudbank

> **Prices change.** Re-check every row against current AWS on-demand prices when the slide is revised. The slide's `slide.md` lists the figures and sources.

Round-number prices in two columns, Compute (laptop-class VM, workstation, A10G GPU) and Storage and data (hot storage, cold archive, egress), each with a concrete example, and a callout on what a $1/hour machine costs if left on for a month. No params; eject to customise.

```markdown
---
id: costs
use: catalog/cb-rule-of-thumb-costs
---
```

---

### `cb-sensitive-data` — Sensitive and regulated data
**Kind:** parameterized · **Brand:** cloudbank

> **Check with CloudBank.** The rules for regulated data change, and so does what CloudBank offers for it. The slide's `slide.md` lists the sources.

Answers "can I put sensitive data in a CloudBank account?": "Know your data's rules" (health records under HIPAA, NIH controlled-access data, federal and export-controlled data, other data under an IRB protocol or data use agreement) and three steps under "Before you upload" (read the rules, ask your institution, talk to CloudBank early).

| Param | Required | Default |
|-------|----------|---------|
| `local-contact` | no | hidden when empty |

```markdown
---
id: sensitive-data
use: catalog/cb-sensitive-data
params:
  local-contact: "Here: the research compliance office, compliance.example.edu"
---
```

---

### `cb-getting-help` — Learning and support
**Kind:** parameterized · **Brand:** cloudbank

Where to get help, for the end of a CloudBank talk: "Learn on your own" (video tutorials, the CloudBank Catalog) and "Ask a person" (monthly office hours, the community forum), each with its web address, and help@cloudbank.org in a band at the bottom.

| Param | Required | Default |
|-------|----------|---------|
| `next-office-hours` | no | hidden when empty |

```markdown
---
id: getting-help
use: catalog/cb-getting-help
params:
  next-office-hours: "Next: Wednesday, November 18"
---
```

---

## Adding new catalog slides

See [CURATION.md](CURATION.md) for the full process. In brief:

1. Create `catalog/slides/<id>/` with `slide.html` and `slide.md`.
2. Add an entry to `catalog/catalog.yml`.
3. Open a PR. The slide owner approves the wording before it is merged; a slide in the catalog is ready to use.
