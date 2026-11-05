---
id: cb-what-is
description: "What CloudBank is: a diagram of how it sits between you and the commercial clouds, plus who runs it, the 2025 NSF award and the NAIRR link"
kind: verbatim
brand: cloudbank
version: "1.1.0"
owner: aaarendt
---

# Description

What CloudBank is, built around a diagram of where it sits: **You** (a
researcher or educator with an ACCESS or NAIRR Pilot award) → **CloudBank**
(sets up your accounts, pays the bills from your award and tracks spending) →
**The clouds** (AWS, Google Cloud, Microsoft Azure, IBM Cloud). The point it
makes is that CloudBank is not a cloud itself. Below the diagram, three facts:
since 2019 (who runs it), CloudBank 2.0 (the 2025 NSF award) and the NAIRR
interface.

The diagram is HTML text in boxes with small line icons and arrows drawn in
the slide (inline SVG, decorative, `aria-hidden`), so every label follows the
font-size minimum and screen readers read it in order: you, CloudBank, the
clouds. No provider logos or outside artwork. The CloudBank box is Deep Navy
so the eye lands on it.

Version 1.1.0 replaces the four-card layout of 1.0.0. Its "Cloud providers"
card became the right-hand box of the diagram; the other three cards are the
facts row, with "NSF-funded cloud access entity" shortened to "Run by".

The on-slide text is condensed to fit the 1.5rem minimum font size. The
original wording is in the speaker notes (presenter view), so the presenter
can quote it exactly.

## Tags

cloudbank, overview, about, diagram, nsf, nairr, program

## Pending

- Four clouds or five. The diagram shows the four named in 1.0.0; the
  CloudBank Catalog also lists Oracle Cloud Infrastructure. Confirm with
  CloudBank before adding a fifth box.

## Sources

Version 1.0.0 was accepted by the slide owner on 2026-11-02, condensed from
the first two pages below. The CloudBank box in the 1.1.0 diagram ("sets up
your accounts, pays the bills from your award and tracks spending") is from
the ACCESS CloudBank Research page: the portal creates accounts after
onboarding, applies charges against the allocation and sends spend alerts. CloudBank's program details change: re-check the slide when they
do, and bump `version` if the wording changes.

- SDSC news, "NSF awards $20M to CloudBank" (April 2025): https://www.sdsc.edu/news/2025/PR20250409-CloudBank.html
- NSF news, "NSF expands access to advanced cloud computing for scientific research": https://www.nsf.gov/news/nsf-expands-access-advanced-cloud-computing-scientific
- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905

## Usage

```markdown
---
id: what-is
use: catalog/cb-what-is
---
```

No parameters. This slide is verbatim: to customise the wording for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . what-is --catalog=<plugin>/catalog
```
