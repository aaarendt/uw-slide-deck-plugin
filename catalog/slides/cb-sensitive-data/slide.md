---
id: cb-sensitive-data
description: "Sensitive and regulated data in CloudBank: which rules apply (HIPAA health records, NIH controlled-access data, federal and export-controlled data, data use agreements) and three steps before uploading"
kind: parameterized
brand: cloudbank
version: "1.0.0"
owner: aaarendt
params:
  local-contact: ""
---

# Description

Answers the question asked at almost every CloudBank talk: can I put
sensitive data, such as health records, in a CloudBank account? The answer on
the slide is "yes, but not by default": the rules come with the data, not with
the cloud. Place it after the how-to-apply slides (`cb-process`, `cb-nairr`)
and before `cb-getting-help`.

The left column, "Know your data's rules", lists four common cases as labelled
rows, each with what it requires. The right column, "Before you upload", gives
three numbered steps: read the rules, ask your institution, talk to CloudBank
early. The health-records row also notes that de-identified data may fall
outside HIPAA. Each rule's label runs inline with its text, as the steps do on
`cb-nairr`, so the slide fits at 1280×720 and 1024×768.

The slide avoids acronyms the audience may not know: "a signed agreement with
the cloud provider" instead of BAA, "NIH's security standard" instead of NIST
SP 800-171, "federal" instead of CUI. The speaker notes give the formal names.

## Pending

**Not ready to merge.** These claims need confirmation from CloudBank before
the slide is used in a talk. The speaker notes mark the same points.

- Whether a standard CloudBank account can hold HIPAA health data at all, and
  whether CloudBank has business associate agreements with the cloud
  providers. Until confirmed, the slide does not say either way.
- Step 3: "Its partners run regulated projects in managed, compliant
  environments." This means Sherlock at the San Diego Supercomputer Center,
  named in the speaker notes. The ACCESS resource page says regulated data is
  supported for "a limited number of projects" through Sherlock services.
- Whether those projects are limited in number, who qualifies, and whether
  Sherlock's management costs come out of the allocation.
- Where to send a regulated-data request (help@cloudbank.org or another
  contact). If there is a dedicated address, add it to step 3.

## Parameters

- `local-contact` (optional): One line under step 2 naming the office to
  contact at the host institution, for example
  `"Here: the research compliance office, compliance.example.edu"`. Check it before the
  talk. Default: `""` (hidden when empty).

## Tags

cloudbank, sensitive-data, regulated-data, hipaa, nih, genomic, cui, export-control, ferpa, irb, compliance, security

## Sources

Drafted on 2026-11-03 from the pages below.

- "Regulated data is supported" for "a limited number of projects" through
  Sherlock services: ACCESS resource pages for CloudBank.
- Sherlock's managed environments (HIPAA, FISMA, controlled unclassified
  information, FERPA; on AWS, Azure, Google Cloud; access control, encryption,
  monitoring, audit support): Sherlock services page.
- Health records: a business associate agreement accepted per account (AWS
  Artifact), and protected health information only in HIPAA-eligible services:
  AWS HIPAA compliance page. "Your university's agreement may not cover a
  CloudBank account" is an inference from the per-account agreement; confirm.
- NIH controlled-access data: NOT-OD-24-157, effective January 25, 2025,
  requires NIST SP 800-171 for institutional, third-party and cloud systems
  holding controlled-access human genomic data, with an attestation in new or
  renewed data use certifications.
- CloudBank's compliance guidance (plan the resources, involve the provider's
  compliance team, CloudBank helps awardees with a compliance plan): CloudBank
  resources, security design pattern.

Bump `version` whenever the wording changes. Re-check the NIH and provider
pages when the slide is revised; these rules change.

- ACCESS Operations, "CloudBank Cloud Resource Provider": https://operations.access-ci.org/node/890
- ACCESS Operations, "CloudBank Research": https://operations.access-ci.org/node/905
- Sherlock, "Compliance in the cloud": https://sherlock.sdsc.edu/services
- AWS, "HIPAA compliance": https://aws.amazon.com/compliance/hipaa-compliance
- NIH Security Best Practices for Users of Controlled-Access Data: https://sharing.nih.gov/sites/default/files/flmngr/NIH-Security-BPs-for-Users-of-Controlled-Access-Data.pdf
- Stanford ORA summary of the NIH requirements: https://ora.stanford.edu/data-use-agreements/nih-security-best-practices-users-controlled-access-data
- CloudBank resources, "Security": https://cloudbank-project.github.io/cb-resources/patterns/security

## Usage

```markdown
---
id: sensitive-data
use: catalog/cb-sensitive-data
params:
  local-contact: "Here: the research compliance office, compliance.example.edu"
---
```

To customise beyond `local-contact`, eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . sensitive-data --catalog=<plugin>/catalog
```
