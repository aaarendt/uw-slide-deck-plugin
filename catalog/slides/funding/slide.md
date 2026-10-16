---
id: funding
description: "Funding credit slide — agency, grant ID, grant title, disclaimer"
kind: parameterized
brand: uw
version: "1.0.0"
status: draft
in_agenda: false
owner: plugin
params:
  agency: "PLACEHOLDER AGENCY"
  grant-id: "PLACEHOLDER GRANT ID"
  grant-title: "PLACEHOLDER GRANT TITLE"
  disclaimer: "Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the funding agency."
---

# Description

Funding acknowledgement slide. The default wording is a **placeholder** and
must be replaced with the exact language required by the funding agency's
award terms. Consult the UW Office of Sponsored Programs (OSP) for guidance.

## Parameters

- `agency` (required): Funding agency name (e.g. `"National Science Foundation"`). Default: placeholder.
- `grant-id` (required): Award or grant number. Default: placeholder.
- `grant-title` (optional): Grant or project title. Default: placeholder.
- `disclaimer` (optional): Disclaimer paragraph; use the exact language from the award. Default: generic NSF-style disclaimer (placeholder only).

## Tags

funding, acknowledgement, uw, framing

## Status note

`status: draft` — default parameter values are placeholders. Change to
`status: ready` only after the wording has been reviewed against the specific
award's requirements.

## Usage

```markdown
---
id: funding
use: catalog/funding
params:
  agency: "National Science Foundation"
  grant-id: "OAC-1234567"
  grant-title: "CloudBank: Enabling Research and Education in the Public Cloud"
---
```

Use the funding agency's required disclaimer text. Do not rely on the default.
