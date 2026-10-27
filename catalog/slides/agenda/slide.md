---
id: agenda
description: "Auto-generated agenda built from deck.yml slide titles and durations"
kind: derived
brand: any
version: "1.1.0"
status: ready
in_agenda: false
owner: plugin
params:
  heading: "Agenda"
---

# Description

Derived slide that generates an agenda automatically from the deck's
`deck.yml` and briefs, in deck order.

## Parameters

- `heading` (optional): The slide's heading text. Default: `"Agenda"`.

## Behaviour

**What is listed.** Every slide except:
- the agenda itself, and slides with `layout: title` or `layout: closing`;
- slides whose brief has `section: hidden`;
- catalog slides marked `in_agenda: false` in their `slide.md` (the framing
  slides: title, land acknowledgement, funding, agenda, feedback, thank you).

**Grouping.** An agenda reads best as a handful of parts, not every slide:
1. If any brief sets `section:`, consecutive slides with the same section
   become one item named after the section (section-divider slides are then
   skipped, since the sections already name the parts).
2. Otherwise, if the deck has `section-divider` slides, each divider and the
   slides after it become one item named after the divider.
3. Otherwise each slide is its own item.

Slides outside any group are listed on their own. A group's minutes are the
sum of the `duration:` values its slides set; minutes are shown only when set.

**Labels.** A slide's `title`, else (for a catalog slide) its heading, else the
first line of its key message, else its ID. Set `title:` on briefs whose key
message is a long sentence.

**Fit.** Up to 7 items in one column, up to 12 in two balanced columns. Past
12 the resolver shows 11 and an "and N more" item, and warns: group the slides
with `section:` to fix it.

## Tags

agenda, structure, framing

## Usage

```markdown
---
id: agenda
use: catalog/agenda
---
```

The agenda is generated at resolution time. Re-run the resolver after
changing slide titles or durations.
