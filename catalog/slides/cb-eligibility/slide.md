---
id: cb-eligibility
description: "CloudBank eligibility (who can lead a project) and recommended uses (good fit vs. better elsewhere)"
kind: verbatim
brand: cloudbank
version: "1.0.0"
status: review
owner: aaarendt
---

# Description

Who can lead a CloudBank project and which workloads CloudBank is meant for.
A shaded strip states the two entry criteria (who and what); below it, two
columns contrast good-fit workloads with workloads better run on on-premises
ACCESS or NAIRR resources. Sources are linked in the footer line.

## Content source

- Adapted from slide 8 of the CloudBank 10-minute workshop overview deck.
- Eligibility: ACCESS allocations policy,
  https://allocations.access-ci.org/allocations-policy#eligibility
- Recommended uses: CloudBank, "Request access to commercial cloud resources",
  https://www.cloudbank.org/request-access-commercial-cloud-resources

The on-slide text is condensed to meet the catalog's 1.5rem minimum font size
and layout word limits. The full original wording of both sources is kept,
verbatim, in the speaker notes (`<aside class="notes">`, shown in presenter
view), so the presenter can quote it exactly.

## Changes from the original slide

- Seven long bullets → five short "good fit" items plus a separate
  "better elsewhere" column, so the exclusion reads as a contrast, not a
  footnote.
- "Must have a scientific focus" moved from the bullet list into the entry
  criteria strip, because it is a requirement, not a use.
- CloudBank logo dropped. A logo on every CloudBank slide belongs in the
  brand's shared header, not in individual catalog slides.
- Google Analytics tracking parameters removed from the ACCESS link.

## Tags

cloudbank, eligibility, access, allocations, recommended-uses, program

## Status note

`status: review`. Eligibility and recommended uses are program policy and can
change. Before setting `status: ready`, the owner checks both source pages
and confirms the condensed wording still matches. Re-check whenever the
ACCESS policy or CloudBank's request page changes, and bump `version`.

## Usage

```markdown
---
id: eligibility
use: catalog/cb-eligibility
---
```

No parameters. This slide is verbatim: to customise the wording for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . eligibility
```
