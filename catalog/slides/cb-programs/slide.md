---
id: cb-programs
description: "CloudBank's six standard services: no cost, helpdesk, accounts, multiple clouds, monitoring, training"
kind: verbatim
brand: cloudbank
version: "1.0.0"
status: review
owner: aaarendt
---

# Description

Six services CloudBank provides, in a two-column grid of short headed items. Each has an original line icon (inline SVG, decorative, `aria-hidden`) in a tinted circle. No logos and no copied artwork.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
original wording is in the speaker notes (presenter view), so the presenter
can quote it exactly.

## Tags

cloudbank, services, programs, helpdesk, monitoring, training, program

## Status note

`status: review`. Program facts; the owner checks them against the current pages before
setting `status: ready`.

Source pages consulted:

- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- ACCESS announcement, "CloudBank Expands Commercial Cloud Access for U.S. Researchers and Educators": https://support.access-ci.org/node/11714

Confirmed against those pages: access through ACCESS and the NAIRR Pilot,
account creation and sign-in with ACCESS credentials, automated spend alerts,
multi-cloud access, and expert support and training resources.

Not found on the pages above, so carried over unchanged from the earlier
wording: "no cost" wording, helpdesk cost estimates, "pay by use charge
model", email balance alerts, cost optimization recommendations for unused or
underutilized resources, and the curated training videos. The cloudbank.org
pages could not be reached from this environment, so the owner should check
these there.

## Usage

```markdown
---
id: programs
use: catalog/cb-programs
---
```

No parameters. This slide is verbatim: to customise the wording for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . programs --catalog=<plugin>/catalog
```
