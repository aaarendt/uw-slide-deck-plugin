---
id: agenda
description: "Auto-generated agenda built from deck.yml slide titles and durations"
kind: derived
brand: any
version: "1.0.0"
status: ready
owner: plugin
params:
  heading: "Agenda"
---

# Description

Derived slide that generates an agenda list automatically from the deck's
`deck.yml`. The resolver reads the slide list and extracts the `title` field
from each brief (falling back to the brief `id` when `title` is absent).
Slides whose briefs have `section: hidden` are excluded.

The agenda lists:
- each slide's title (or id) on one line
- duration in minutes if the brief has a `duration:` field

## Parameters

- `heading` (optional): The slide's heading text. Default: `"Agenda"`.

## Behaviour

- Structural slides (`layout: title`, `layout: section-divider`, `layout: closing`) are excluded from the agenda list.
- The agenda slide itself is also excluded.
- Content slides are listed in deck order.
- Duration minutes are shown only when set on the brief.

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
