# Slide Catalog

Vetted, reusable slides that any deck can reference by ID. The catalog keeps framing slides (title, land acknowledgement, agenda, closing) consistent across trainings without copying HTML between decks.

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

The catalog resolver copies the slide's HTML into `content/<deck-id>.html`, rewrites its ID and CSS selectors to match your deck, and substitutes your params. Run it from inside the deck directory:

```bash
python3 tools/resolve-catalog.py resolve .
```

`/uw-slides:generate-slides` calls this automatically for any slide with `use: catalog/...`.

### Ejecting a catalog slide

To customise a catalog slide beyond its params, eject it — this copies the resolved HTML into the deck as a locked slide and removes the `use:` reference:

```bash
python3 tools/resolve-catalog.py eject . <slide-id>
```

After ejecting, edit `content/<id>.html` directly and set `locked: true` in the brief.

---

## Available slides

### `uw-title` — Title slide
**Kind:** parameterized · **Brand:** uw · **Status:** ready

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

### `land-ack` — Land acknowledgement
**Kind:** verbatim · **Brand:** uw · **Status:** draft ⚠

> **The text in this slide is a placeholder.** Replace it with the current approved wording from the UW Office of Minority Affairs & Diversity (OMA&D) or the Office of the President before use. Do not present this slide with placeholder text.

No params. To customise the wording, eject the slide and edit the HTML directly.

```markdown
---
id: land-ack
use: catalog/land-ack
---
```

---

### `funding` — Funding credit
**Kind:** parameterized · **Brand:** uw · **Status:** draft ⚠

> **Default param values are placeholders.** Use the exact language required by the award. Consult the UW Office of Sponsored Programs (OSP) if unsure.

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
**Kind:** derived · **Brand:** any · **Status:** ready

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
**Kind:** parameterized · **Brand:** any · **Status:** ready

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
**Kind:** parameterized · **Brand:** any · **Status:** ready

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

### `cb-eligibility` — CloudBank eligibility and recommended uses
**Kind:** verbatim · **Brand:** cloudbank · **Status:** review ⚠

> **Program policy wording.** Check the condensed text against the ACCESS allocations policy and CloudBank's request-access page before setting `status: ready`, and again whenever either changes.

Who can lead a project and what CloudBank is for: a who/what criteria strip, then "Good fit" and "Better elsewhere" columns. The full original wording of both sources is in the speaker notes. No params; eject to customise.

```markdown
---
id: eligibility
use: catalog/cb-eligibility
---
```

---

### `cb-what-is` — CloudBank overview
**Kind:** verbatim · **Brand:** cloudbank · **Status:** review ⚠

> **Program policy wording.** Check the condensed text against CloudBank's current pages before setting `status: ready`. The slide's `slide.md` lists the pages checked and the facts still unverified.

Four cards: origin, cloud providers, the 2025 CloudBank 2.0 award, and the NAIRR interface role. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: what-is
use: catalog/cb-what-is
---
```

---

### `cb-programs` — CloudBank programs
**Kind:** verbatim · **Brand:** cloudbank · **Status:** review ⚠

> **Program policy wording.** Check the condensed text against CloudBank's current pages before setting `status: ready`. The slide's `slide.md` lists the pages checked and the facts still unverified.

Six short headed items: no cost, consulting and helpdesk, account management, multiple clouds, monitoring and optimization, training. No icons or logos. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: programs
use: catalog/cb-programs
---
```

---

### `cb-why-choose` — Why choose CloudBank for an account
**Kind:** verbatim · **Brand:** cloudbank · **Status:** review ⚠

> **Program policy wording.** Check the condensed text against CloudBank's current pages before setting `status: ready`. The slide's `slide.md` lists the pages checked and the facts still unverified.

Three reasons (no card or purchase agreement, one bill for several clouds, cost monitoring and spending cap) and a callout that awards are grant dollars, not credits. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: why-choose
use: catalog/cb-why-choose
---
```

---

### `cb-award-tiers` — Grant award tiers
**Kind:** verbatim · **Brand:** cloudbank · **Status:** review ⚠

> **Program policy wording.** Check the condensed text against CloudBank's current pages before setting `status: ready`. The slide's `slide.md` lists the pages checked and the facts still unverified.

A table of Explore, Discover and Accelerate with range, average and typical use, plus three facts. **The figures are unverified**; see the slide's status note. The full original wording is in the speaker notes. No params; eject to customise.

```markdown
---
id: award-tiers
use: catalog/cb-award-tiers
---
```

---

### `cb-process` — Application-to-account process
**Kind:** verbatim · **Brand:** cloudbank · **Status:** review ⚠

> **Program policy wording.** Check the condensed text against CloudBank's current pages before setting `status: ready`. The slide's `slide.md` lists the pages checked and the facts still unverified.

Five numbered steps from estimating costs to using the clouds. The full original wording is in the speaker notes. No params; eject to customise.

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
3. Open a PR; the slide owner reviews it before it is marked `status: ready`.
