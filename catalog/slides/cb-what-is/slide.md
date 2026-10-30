---
id: cb-what-is
description: "What CloudBank is: who runs it, which clouds, the 2025 NSF award and the NAIRR link"
kind: verbatim
brand: cloudbank
version: "1.0.0"
status: review
owner: aaarendt
---

# Description

Four-card overview of what CloudBank is: its origin, the cloud providers it brokers, the CloudBank 2.0 award, and its role as the NAIRR Pilot's interface for private-sector cloud contributions.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
original wording is in the speaker notes (presenter view), so the presenter
can quote it exactly.

## Tags

cloudbank, overview, about, nsf, nairr, program

## Status note

`status: review`. Program facts; the owner checks them against the current pages before
setting `status: ready`.

Source pages consulted:

- SDSC news, "NSF awards $20M to CloudBank" (April 2025): https://www.sdsc.edu/news/2025/PR20250409-CloudBank.html
- NSF news, "NSF expands access to advanced cloud computing for scientific research": https://www.nsf.gov/news/nsf-expands-access-advanced-cloud-computing-scientific

Confirmed against those pages: the $20M award, five-year horizon, about 500
projects a year, the four providers, and the NAIRR Pilot interface role.

Flagged, not resolved:

- **Who leads.** The earlier wording said CloudBank is "co-led by" UC San Diego
  (SDSC), UC Berkeley and UW eScience. NSF says it is "led by the San Diego
  Supercomputer Center and Information Technology Services Division at UC San
  Diego" in partnership with UC Berkeley and the University of Washington. The
  slide names the three institutions without saying who leads. The owner
  decides the wording. The speaker notes keep the original "co-led" text.
- **Providers.** The NSF page also lists NVIDIA DGX Cloud next to the four
  clouds on this slide.
- **Eligibility.** The notes say "any U.S. researcher or educator at academic,
  non-profit research, or educational institutions". The pages above do not
  state that list (the NSF page stresses institutions with limited resources),
  so the slide does not repeat it. Eligibility is on `cb-eligibility`.
- **"Since 2019"** is not stated on these pages; SDSC says the pilot is "now in
  its sixth year of operation".
- **Shared portal** and **billing support** (in the notes) were not found on
  these pages.

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
