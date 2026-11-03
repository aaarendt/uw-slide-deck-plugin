---
id: cb-nairr
description: "CloudBank through the NAIRR Pilot: how it differs from ACCESS (AI focus, all-U.S. team, cash awards, longer review) and the portal's three routes"
kind: verbatim
brand: cloudbank
version: "1.0.0"
owner: aaarendt
---

# Description

The second route to a CloudBank account, the NAIRR Pilot, and how it
differs from ACCESS. Meant to follow `cb-process` (the ACCESS route) or
`cb-research-and-classroom`.

The left column lists four differences from ACCESS as labelled rows (focus,
who, awards, review). The right column lists the three routes on the NAIRR
Pilot portal as shaded cards (researcher resources, classroom resources, data
and models), with the portal address below them. The portal is drawn in HTML
and CSS: the NSF screenshot on the source slide is not included, so the slide carries no third-party artwork.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
speaker notes give the full wording, including the 12-month project length and
the 2026 NAIRR Operations Center award.

## Tags

cloudbank, nairr, nairr-pilot, ai, access, allocations, eligibility, program

## Sources

Adapted from a CloudBank slide supplied by the slide owner on 2026-11-03.
Checked against the pages below on 2026-11-03.

- "AI focus", "U.S.-based", the monthly review cycle, the 12-month project
  length and the three portal routes: NAIRR Pilot pages.
- "Everyone on the project, not just the lead" and "early awards were in
  credits, now cash awards": from the slide owner. The NAIRR Pilot pages do
  not state either; the ACCESS CloudBank Research page states that CloudBank
  awards are made in dollars.
- The ACCESS comparison ("under a week") comes from `cb-process`.

The NAIRR Pilot pages now say "SI" (super intelligence) where they used to
say "AI". This slide keeps "AI" throughout, by the slide owner's decision on
2026-11-03; do not switch it when re-checking against those pages.

Re-check when NAIRR moves from the pilot to the NAIRR Operations Center
(awarded September 2026): the portal address and the word "Pilot" may change.
Bump `version` whenever the wording changes.

- NAIRR Pilot, "Resource Requests": https://nairrpilot.org/allocations
- NAIRR Pilot home page (portal routes, Operations Center notice): https://nairrpilot.org/
- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- CloudBank user guide, "NAIRR Pilot CloudBank for Classroom": https://www.cloudbank.org/training/nairr-pilot-cloudbank-classroom

## Usage

```markdown
---
id: nairr
use: catalog/cb-nairr
---
```

No parameters. This slide is verbatim: to customise the wording for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . nairr --catalog=<plugin>/catalog
```
