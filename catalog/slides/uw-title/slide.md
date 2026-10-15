---
id: uw-title
description: "Standard UW branded title slide with presenter info"
kind: parameterized
brand: uw
version: "1.0.0"
status: ready
owner: plugin
params:
  title: "Presentation Title"
  subtitle: ""
  presenter: ""
  affiliation: "University of Washington"
  date: ""
---

# Description

Standard opening title slide with a dark UW purple background, the gold accent
bar, and a three-section layout: an optional logo area at the top, the
presentation title and subtitle in the centre, and presenter details at the
bottom.

## Parameters

- `title` (required): Main presentation title shown large. Default: `"Presentation Title"`.
- `subtitle` (optional): Shown below the title in muted text. Default: `""` (hidden when empty).
- `presenter` (optional): Presenter name. Default: `""`.
- `affiliation` (optional): Institutional affiliation. Default: `"University of Washington"`.
- `date` (optional): Date string; quote dates in the brief. Default: `""`.

## Tags

title, uw, framing, opening

## Usage

In a deck brief:

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
