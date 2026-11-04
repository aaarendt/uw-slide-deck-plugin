---
id: cb-rule-of-thumb-costs
description: "Rule-of-thumb cloud prices: laptop-class VM, workstation, A10G GPU, hot and cold storage, data egress, and what a machine left on for a month costs"
kind: verbatim
brand: cloudbank
version: "1.1.0"
owner: aaarendt
---

# Description

Round-number prices for estimating cloud costs, so an audience can size a
project before opening a cost calculator. Two columns of price rows: Compute
(laptop-class virtual machine, powerful workstation, a machine with an NVIDIA
A10G GPU) and Storage and data (hot object storage, cold archive, data
egress). Each row shows the price large, then what it buys and a concrete
example (machine size, or the cost of a terabyte). A shaded callout below
gives the cost of a $1/hour machine left on for a month, the most common
source of surprise bills. Pairs well before `cb-process`, whose first step is
estimating costs, and answers the surprise-bill quote in `cb-what-weve-heard`.

The speaker notes name the example instance types, explain spot pricing and
GPU quotas, and add retrieval and upload details.

## Tags

cloudbank, costs, pricing, budget, estimate, gpu, storage, egress, program

## Sources

Adapted from a slide supplied by the slide owner on 2026-11-03. Prices checked
on 2026-11-03 against AWS on-demand prices in US East (N. Virginia), using the
AWS price list of 2026-09-28 as reported by the pages below.

- Hot object storage: S3 Standard, first 50 TB, $0.023/GB-month.
- Cold archive: S3 Glacier Deep Archive, $0.00099/GB-month.
- Data egress: data transfer out to the internet, first 10 TB, $0.09/GB after
  the first 100 GB a month free. Added to the owner's list; not on the
  source slide.
- Laptop-class VM: m7i.large (2 vCPUs, 8 GiB), $0.1008/hour.
- Workstation: m7i.4xlarge (16 vCPUs, 64 GiB), $0.8064/hour.
- A10G GPU: g5.xlarge (4 vCPUs, 16 GiB, 1 A10G), $1.006/hour on demand; spot
  $0.46 to $0.60/hour across us-east-1 zones. The source slide said about
  $2/hour on demand and $0.20 spot; the slide uses the current figures.
- The $730 callout: $1/hour × 730 hours (an average month).

Prices change. Re-check every row when the slide is revised and bump
`version` if any figure changes.

- Amazon S3 pricing: https://aws.amazon.com/s3/pricing/
- Amazon EC2 on-demand pricing: https://aws.amazon.com/ec2/pricing/on-demand/
- Upstash, "AWS S3 Pricing Explained (2026)" (October 2026 figures): https://upstash.com/blog/aws-s3-pricing-explained-2026
- DoiT, g5.xlarge in us-east-1 (on-demand and spot): https://www.doit.com/compute/compute/aws/us-east-1/g5.xlarge
- DoiT, m7i.large in us-east-1 (also lists m7i.4xlarge): https://www.doit.com/compute/spot/us-east-1/m7i.large

## Usage

```markdown
---
id: costs
use: catalog/cb-rule-of-thumb-costs
---
```

No parameters. This slide is verbatim: to customise the prices for one deck,
eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . costs --catalog=<plugin>/catalog
```
