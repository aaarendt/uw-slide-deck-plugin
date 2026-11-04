---
id: cb-why-choose
description: "What you get with a CloudBank account: billing handled (no card, one bill, spending cap, grant dollars) and accounts handled (set up for you, one login, collaborators, add clouds later)"
kind: verbatim
brand: cloudbank
version: "2.0.0"
owner: aaarendt
---

# Description

"What you get with a CloudBank account", in two columns of four headed items,
each with an original line icon (inline SVG, decorative, `aria-hidden`) in a
tinted circle. No provider logos.

- **Billing, handled for you:** no credit card (NSF pays through the ACCESS or
  NAIRR Pilot award), one bill across several clouds, a spending cap with
  alerts and tips on idle resources, and dollars rather than credits, so the
  award also pays for marketplace software and AI model access.
- **Accounts, handled for you:** accounts set up after onboarding, one login
  (ACCESS credentials) to each cloud, collaborators managed in one place, and
  another cloud added to the project later.

Both columns answer "why get cloud through CloudBank rather than directly from
a provider?". General cloud capabilities (AI models, hosting, data access)
belong on `cb-why-cloud`, not here.

Version 2.0.0 merges the former `cb-programs` slide into this one. Its help
and training items moved to `cb-getting-help`; its account, monitoring and
multiple-cloud items are here. The heading changed from "Why choose CloudBank
for an account?".

The speaker notes also mention Globus for moving large datasets between
campus and cloud storage.

## Tags

cloudbank, benefits, billing, marketplace, spending-cap, accounts, login, collaborators, program

## Pending

- The number of clouds. The slide says "all the clouds CloudBank offers"
  without naming them. The speaker notes name four (AWS, Google Cloud, Azure,
  IBM Cloud), but the CloudBank Catalog also lists Oracle Cloud
  Infrastructure. Confirm with CloudBank, then name them here and in
  `cb-what-is`.
- What happens to running resources at the spending cap, and to stored data
  when the allocation ends. The speaker notes mark this; add a line once known.

## Sources

Version 1.0.0 (no card, one bill, spending cap, grant dollars) and the former
`cb-programs` (no cost, account management, monitoring and optimization) were
accepted by the slide owner on 2026-11-02. Version 2.0.0, drafted on
2026-11-03, merges them. The account items come from the ACCESS resource
pages: the portal creates cloud accounts for the platforms in the request and
more can be added later, users sign in with their ACCESS credentials
(federated login), and the project manages which authorized ACCESS users can
use each account. CloudBank's program details change: re-check the slide when
they do, and bump `version` if the wording changes.

- ACCESS resource page, "CloudBank Research": https://operations.access-ci.org/node/905
- ACCESS resource page, "CloudBank Cloud Resource Provider": https://operations.access-ci.org/node/890
- ACCESS announcement: https://support.access-ci.org/node/11714

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
