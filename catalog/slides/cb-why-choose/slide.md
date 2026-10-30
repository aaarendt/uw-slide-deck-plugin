---
id: cb-why-choose
description: "Why a researcher would choose a CloudBank account: no card, one bill, spending cap, grant dollars"
kind: verbatim
brand: cloudbank
version: "1.0.0"
status: review
owner: aaarendt
---

# Description

Three short reasons to choose a CloudBank account, then a highlighted callout that the awards are grant dollars, not credits, so they cover marketplace services. No diagram or provider logos.

The on-slide text is condensed to fit the 1.5rem minimum font size. The
original wording is in the speaker notes (presenter view), so the presenter
can quote it exactly.

## Tags

cloudbank, benefits, billing, marketplace, spending-cap, program

## Status note

`status: review`. Program policy wording; the owner checks it against the current pages before
setting `status: ready`.

Source pages consulted:

- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- ACCESS announcement: https://support.access-ci.org/node/11714

Confirmed: awards are made in dollars and usable on AWS, Google Cloud, IBM
Cloud and Microsoft Azure; usage is tracked continuously with automated spend
alerts.

Not confirmed (cloudbank.org pages could not be reached from this
environment), carried over unchanged from the earlier wording:

- no credit card or university purchase agreement required
- a spending cap (the pages above mention spend alerts, not a cap)
- grant dollars can be used for marketplace services, third-party
  applications and LLM model access

Also check how "grant dollars, not credits" sits next to the process slide,
where ACCESS credits are exchanged for CloudBank dollars.

## Usage

```markdown
---
id: why-choose
use: catalog/cb-why-choose
---
```

No parameters. This slide is verbatim: to customise the wording for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . why-choose --catalog=<plugin>/catalog
```
