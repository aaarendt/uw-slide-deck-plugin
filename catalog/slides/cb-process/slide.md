---
id: cb-process
description: "CloudBank onboarding process in five steps, from cost estimate to using the clouds, in under a week"
kind: verbatim
brand: cloudbank
version: "1.0.0"
status: review
owner: aaarendt
---

# Description

A left-to-right flow of five numbered steps from estimating costs to using commercial cloud accounts, drawn in HTML and CSS with arrows between steps. A text tag under each step (ACCESS, CloudBank, Providers) shows which system it happens in, replacing the logos used in the program's own diagram. The last step condenses three actions: manage users in ACCESS, assign them to cloud accounts in the CloudBank Portal, and use the clouds at the providers' portals. Step detail is in the speaker notes.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
original wording is in the speaker notes (presenter view), so the presenter
can quote it exactly.

## Tags

cloudbank, process, onboarding, access, allocation, steps, program

## Status note

`status: review`. Program process wording; the owner checks it against the current pages before
setting `status: ready`.

Source pages consulted:

- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- ACCESS announcement: https://support.access-ci.org/node/11714

Confirmed: accounts are created for the platforms in the request, more can be
added later, and users are managed through the portal with ACCESS credentials;
CloudBank is allocated through ACCESS and the NAIRR Pilot.

Flagged, not confirmed (cloudbank.org pages could not be reached from this
environment): the **"under a week" turnaround** in the title, the calculator
and ACCESS-credit-to-CloudBank-dollar exchange steps, and the onboarding email.
The ACCESS resource page points to the CloudBank user guide
(https://www.cloudbank.org/training/access-cloudbank-research) for process
details; the owner should check the slide against it.

No ACCESS or CloudBank logos appear on the slide, per the catalog's no-logos rule for individual slides.

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
python3 tools/resolve-catalog.py eject . process
```
