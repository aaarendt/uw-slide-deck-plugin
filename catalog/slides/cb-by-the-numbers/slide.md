---
id: cb-by-the-numbers
description: "CloudBank usage figures: research projects, dollars allocated, classrooms, awards by tier and the top research fields, for a stated period"
kind: parameterized
brand: cloudbank
version: "1.0.0"
owner: aaarendt
params:
  period: "October 2025 to October 2026"
  research-projects: "292"
  allocated: "$2.24M"
  classrooms: "78"
  explore-projects: "234"
  explore-avg: "$4,423"
  discover-projects: "56"
  discover-avg: "$19,689"
  accelerate-projects: "2"
  accelerate-avg: "$52,094"
  more-fields: "40"
---

# Description

Evidence that CloudBank is in use. Three headline stats across the top
(research projects awarded, dollars allocated to research, CloudBank Classroom
classes), then two columns: research awards by tier (projects and average
award for Explore, Discover and Accelerate) and the top three research fields
with a count of the others. Pairs well after `cb-award-tiers`, whose published
averages it puts next to actual ones.

Every figure is a parameter whose default is the current value, because the
numbers change monthly. A deck can show newer figures by setting params in its
brief, without ejecting the slide or waiting for a catalog release. The three
top fields are fixed text: change them by bumping the slide's `version`.

## Parameters

All optional; defaults are the October 2026 figures.

- `period`: the period the figures cover, shown under the heading and in the
  source line. Default: `"October 2025 to October 2026"`.
- `research-projects`: research projects awarded (Explore + Discover +
  Accelerate + Maximize). Default: `"292"`.
- `allocated`: dollars allocated to research, rounded. Default: `"$2.24M"`
  (exact: $2,241,857).
- `classrooms`: CloudBank Classroom allocations. Default: `"78"`.
- `explore-projects`, `explore-avg`: Default: `"234"`, `"$4,423"`.
- `discover-projects`, `discover-avg`: Default: `"56"`, `"$19,689"`.
- `accelerate-projects`, `accelerate-avg`: Default: `"2"`, `"$52,094"`.
- `more-fields`: research fields beyond the top three, excluding "Unknown".
  Default: `"40"`.

## Tags

cloudbank, statistics, metrics, impact, allocations, awards, fields, program

## Sources

Figures supplied by the slide owner on 2026-11-03 from two CloudBank
reporting slides:

- "CloudBank Allocations (Oct'25 - Oct'26)": projects and average award by
  tier (Explore 234 at $4,423, Discover 56 at $19,689, Accelerate 2 at
  $52,094, Maximize 0), CloudBank Classroom 78, total allocated $2,241,857.
  Checked: the tier counts sum to 292 research projects, each tier's count
  times its average gives its total, and the totals sum to $2,241,857.
- "Research Allocations (cont.)": research awards by field, ranked AI and
  intelligent systems, computer science, materials engineering. The chart
  lists 15 categories (one of them "Unknown") and 29 others, so 43 named
  fields: the top three plus 40 more.

Maximize (no awards in this period) is left off the slide; the speaker notes
mention it. Also left off as internal operations detail: the migration of about
100 CloudBank 1 researchers to ACCESS and the transition of about 20 NAIRR
Pilot awards after vendor credits expired on 2026-06-30.

Update the defaults and bump `version` when new figures are published.

## Usage

```markdown
---
id: by-the-numbers
use: catalog/cb-by-the-numbers
---
```

With newer figures:

```markdown
---
id: by-the-numbers
use: catalog/cb-by-the-numbers
params:
  period: "October 2025 to December 2026"
  research-projects: "340"
  allocated: "$2.6M"
---
```

Params not set keep their defaults, so set every figure that changed.

```bash
python3 tools/resolve-catalog.py eject . by-the-numbers --catalog=<plugin>/catalog
```
