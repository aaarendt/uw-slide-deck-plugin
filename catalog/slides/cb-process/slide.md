---
id: cb-process
description: "CloudBank onboarding process: four steps from cost estimate to onboarding, ending with working in the cloud, in under a week"
kind: verbatim
brand: cloudbank
version: "1.0.0"
owner: aaarendt
---

# Description

A left-to-right flow of four numbered steps (estimate costs, request an allocation, exchange credits, onboard), each with a one-sentence description, ending in an unnumbered "Start working in the cloud" card. Drawn in HTML and CSS with arrows between steps. A text tag under each step (ACCESS, CloudBank, Cloud provider) shows which system it happens in, replacing the logos used in the program's own diagram. Managing users and allocations after setup is deliberately left to the speaker notes.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
original wording is in the speaker notes (presenter view), so the presenter
can quote it exactly.

## Tags

cloudbank, process, onboarding, access, allocation, steps, program

## Sources

Accepted by the slide owner on 2026-11-02. The wording was condensed from the
pages below. CloudBank's program details change: re-check the slide when they
do, and bump `version` if the wording changes.

- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- ACCESS announcement: https://support.access-ci.org/node/11714
- CloudBank user guide, "Access CloudBank Research": https://www.cloudbank.org/training/access-cloudbank-research

## Usage

```markdown
---
id: process
use: catalog/cb-process
---
```

No parameters. This slide is verbatim: to customise the wording for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . process --catalog=<plugin>/catalog
```
