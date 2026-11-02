---
id: cb-title
description: "Standard CloudBank branded title slide with presenter info"
kind: parameterized
brand: cloudbank
version: "1.0.0"
in_agenda: false
owner: aaarendt
params:
  title: "Presentation Title"
  subtitle: ""
  presenter: ""
  affiliation: "CloudBank"
  date: ""
---

# Description

Standard opening title slide for CloudBank decks: a dark Deep Navy background,
the Signal Blue accent bar, and a two-section layout with the presentation
title and subtitle in the centre and presenter details at the bottom. It is the
CloudBank counterpart of `uw-title` and takes the same parameters.

## Parameters

- `title` (required): Main presentation title shown large. Default: `"Presentation Title"`.
- `subtitle` (optional): Shown below the title in muted text. Default: `""` (hidden when empty).
- `presenter` (optional): Presenter name. Default: `""` (hidden when empty).
- `affiliation` (optional): Presenter's affiliation. Default: `"CloudBank"`. Set it to the presenter's own institution when that is more accurate.
- `date` (optional): Date string; quote dates in the brief. Default: `""` (hidden when empty).

## Tags

title, cloudbank, framing, opening

## Usage

In a deck brief:

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
