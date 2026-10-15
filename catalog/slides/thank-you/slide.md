---
id: thank-you
description: "Closing thank-you slide with presenter name and contact info"
kind: parameterized
brand: any
version: "1.0.0"
status: ready
owner: plugin
params:
  message: "Thank You"
  action: ""
  presenter: ""
  email: ""
  url: ""
---

# Description

Closing slide with a large thank-you message and optional presenter contact
details (name, email, URL). Use this as the last slide in a deck, or use the
`closing` layout for a call-to-action closing.

## Parameters

- `message` (optional): Main heading. Default: `"Thank You"`.
- `action` (optional): A one-sentence next step or call to action. Default: `""` (hidden when empty).
- `presenter` (optional): Presenter name. Default: `""`.
- `email` (optional): Contact email. Default: `""`.
- `url` (optional): Website or resource URL. Default: `""`.

## Tags

thank-you, closing, framing

## Usage

```markdown
---
id: thank-you
use: catalog/thank-you
params:
  message: "Thank You"
  action: "Launch one VM this week."
  presenter: "Jane Doe"
  email: "jdoe@uw.edu"
  url: "cloudbank.org/resources"
---
```
