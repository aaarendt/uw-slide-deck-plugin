---
id: cb-eligibility
description: "CloudBank eligibility (who can lead a project) and recommended uses (good fit vs. better elsewhere)"
kind: verbatim
brand: cloudbank
version: "1.0.0"
owner: aaarendt
---

# Description

Who can lead a CloudBank project and which workloads CloudBank is meant for.
A shaded strip states the two entry criteria (who and what); below it, two
columns contrast good-fit workloads with workloads better run on on-premises
ACCESS or NAIRR resources. Sources are linked in the footer line.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
full wording of both sources is in the speaker notes (presenter view), so
the presenter can quote it exactly.

## Tags

cloudbank, eligibility, access, allocations, recommended-uses, program

## Sources

Accepted by the slide owner on 2026-11-02. The wording was condensed from the
pages below. CloudBank's program details change: re-check the slide when they
do, and bump `version` if the wording changes.

- ACCESS allocations policy (eligibility): https://allocations.access-ci.org/allocations-policy#eligibility
- CloudBank, "Request access to commercial cloud resources" (recommended uses): https://www.cloudbank.org/request-access-commercial-cloud-resources

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
python3 tools/resolve-catalog.py eject . eligibility --catalog=<plugin>/catalog
```
