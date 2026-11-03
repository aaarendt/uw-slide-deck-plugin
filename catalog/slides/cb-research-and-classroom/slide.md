---
id: cb-research-and-classroom
description: "The two CloudBank offerings side by side: Research (cloud accounts for projects) and Classroom (a JupyterHub for teaching)"
kind: parameterized
brand: cloudbank
version: "1.0.0"
owner: aaarendt
params:
  focus: ""
---

# Description

A comparison of CloudBank's two offerings, so the audience knows they exist
and which one the talk is about. A table with the CloudBank Research and
CloudBank Classroom logos as column headers and three rows: who it is for,
what you get, and how to start. Place it right after `cb-what-is`.

Most CloudBank catalog slides (`cb-eligibility`, `cb-award-tiers`,
`cb-process`) describe Research. Use `focus` to say so, or to point a teaching
audience to Classroom.

The speaker notes add background a presenter can use: the Berkeley Data Stack
and Data 8, the 2i2c partnership with community colleges, teaching AI, and the
HPCwire 2023 award. Hub and student counts are left off the slide because they
change; check them with the CloudBank team before quoting.

## Parameters

- `focus` (optional): One line under the table, for example
  `"The rest of this talk covers CloudBank Research."` Default: `""` (hidden
  when empty).

## Assets

| File | Source |
|------|--------|
| `cloudbank-research.png` | CloudBank Research logo (JPG on white), white made transparent |
| `cloudbank-classroom.png` | CloudBank Classroom logo (PNG), cropped and scaled to 1000 px wide |

## Tags

cloudbank, research, classroom, jupyterhub, teaching, overview, program

## Sources

Accepted by the slide owner on 2026-11-03. The Classroom column is condensed
from the ACCESS pages below and a CloudBank Classroom slide supplied by the
owner. CloudBank's program details change: re-check the slide when they do,
and bump `version` if the wording changes.

- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- ACCESS documentation, "CloudBank Classroom": https://support.access-ci.org/documentation/resources/cloudbank-classroom
- ACCESS resource page, "CloudBank Classroom": https://operations.access-ci.org/node/907

## Usage

```markdown
---
id: research-and-classroom
use: catalog/cb-research-and-classroom
params:
  focus: "The rest of this talk covers CloudBank Research."
---
```

To customise beyond `focus`, eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . research-and-classroom --catalog=<plugin>/catalog
```
