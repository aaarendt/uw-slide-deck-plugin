---
id: land-ack
description: "Land acknowledgement — placeholder text requires approved UW wording"
kind: verbatim
brand: uw
version: "1.0.0"
status: draft
owner: plugin
---

# Description

Land acknowledgement slide. The text in this slide is a **placeholder** and
must be replaced with the approved institutional wording before use.

Contact the UW Office of Minority Affairs & Diversity (OMA&D) or the Office
of the President for the current approved land acknowledgement text.

## Tags

land-acknowledgement, uw, framing, opening

## Status note

`status: draft` — the placeholder wording has not been approved. Change to
`status: ready` only after the text has been reviewed and approved.

## Usage

```markdown
---
id: land-ack
use: catalog/land-ack
---
```

No parameters. This slide is verbatim: to customise the wording, eject it and
edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . land-ack
```
