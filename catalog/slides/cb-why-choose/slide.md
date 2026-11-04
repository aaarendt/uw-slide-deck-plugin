---
id: cb-why-choose
description: "What you get with a CloudBank account: billing handled (no card, one bill, spending cap, grant dollars) and more than virtual machines (shared access, data transfer, AI models, hosting tools and datasets)"
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
- **More than virtual machines:** shared access (ACCESS login, collaborators),
  moving big datasets (Globus), using hosted AI models without GPUs, and
  hosting a tool or dataset for a community (science gateways).

Version 2.0.0 merges the former `cb-programs` slide into this one. Its help
and training items moved to `cb-getting-help`; its account, monitoring and
multiple-cloud items are here. The heading changed from "Why choose CloudBank
for an account?".

The slide names services in plain words; the speaker notes give the product
names (Globus, Amazon Bedrock, Azure AI, Google Vertex AI).

## Tags

cloudbank, benefits, billing, marketplace, spending-cap, accounts, data-transfer, globus, ai, llm, inference, gateways, program

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
2026-11-03, merges them and adds three services that the ACCESS resource pages
list: Globus data transfer and sharing, model inference services, and science
gateway support (community accounts, hosting of data collections, databases,
services and web interfaces). CloudBank's program details change: re-check the
slide when they do, and bump `version` if the wording changes.

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
