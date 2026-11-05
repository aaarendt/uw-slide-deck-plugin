---
id: cb-what-is
description: "CloudBank: A Managed Service to Simplify Cloud Access. A diagram of a researcher, CloudBank (opens accounts, pays from the award, tracks spending) and the commercial clouds, plus who runs it"
kind: verbatim
brand: cloudbank
version: "1.1.0"
owner: aaarendt
---

# Description

"CloudBank: A Managed Service to Simplify Cloud Access", built around one
diagram that shows CloudBank is not a cloud itself. On the left, a
**Researcher** with an ACCESS or NAIRR Pilot award, with an arrow to
**CloudBank**, a Deep Navy box listing what it does, each line led by a teal
arrow: opens your accounts, pays from your award, tracks your spending. The
box stands on the edge of a shaded "Commercial clouds" panel ("where your
work runs"), and lines fan out from it to AWS, Google Cloud, Microsoft Azure
and IBM Cloud. Below the diagram, one line at body size says who runs it: UC
San Diego (SDSC), UC Berkeley and UW eScience, funded by NSF since 2019.

The headline uses CloudBank's own description ("managed services to simplify
cloud access", from the 2021 CloudBank paper) rather than "gateway", which in
ACCESS usually means a science gateway.

All labels are HTML text; the arrows, fan lines, icons and shaded panel are
drawn in the slide (inline SVG and CSS, decorative, `aria-hidden`), so every
label follows the font-size minimum and screen readers read it in order:
researcher, CloudBank and its three tasks, the clouds, who runs it. No
provider logos or outside artwork.

Version 1.1.0 replaces the four-card layout of 1.0.0. The "Cloud providers"
card became the clouds panel and "NSF-funded cloud access entity" became the
"Run by" line. The 2025 CloudBank 2.0 award and the NAIRR interface role moved to the
speaker notes; `cb-by-the-numbers` and `cb-nairr` cover them on their own
slides. The full wording is in the speaker notes (presenter view), so the
presenter can quote it exactly.

## Tags

cloudbank, overview, about, diagram, managed service, nsf, nairr, program

## Pending

- Four clouds or five. The diagram shows the four named in 1.0.0; the
  CloudBank Catalog also lists Oracle Cloud Infrastructure. Confirm with
  CloudBank before adding a fifth row.

## Sources

Version 1.0.0 was accepted by the slide owner on 2026-11-02, condensed from
the first two pages below. The CloudBank box in the 1.1.0 diagram ("sets up
your accounts, pays the bills from your award and tracks spending") is from
the ACCESS CloudBank Research page: the portal creates accounts after
onboarding, applies charges against the allocation and sends spend alerts. The
1.1.0 headline is from the title of the 2021 CloudBank paper (last source
below). CloudBank's program details change: re-check the slide when they
do, and bump `version` if the wording changes.

- SDSC news, "NSF awards $20M to CloudBank" (April 2025): https://www.sdsc.edu/news/2025/PR20250409-CloudBank.html
- NSF news, "NSF expands access to advanced cloud computing for scientific research": https://www.nsf.gov/news/nsf-expands-access-advanced-cloud-computing-scientific
- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- Paper, "CloudBank: Managed Services to Simplify Cloud Access for Computer Science Research and Education" (2021): https://www.escholarship.org/uc/item/9c93d2mh

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
