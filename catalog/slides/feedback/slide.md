---
id: feedback
description: "Session feedback slide with a configurable survey URL"
kind: parameterized
brand: any
version: "1.0.0"
status: ready
in_agenda: false
owner: plugin
params:
  heading: "Share Your Feedback"
  url: ""
  url-label: "feedback survey"
  prompt: "Help us improve this workshop — your response takes about 2 minutes."
---

# Description

A session feedback slide prompting participants to complete a survey. Include
a URL to your feedback form (Google Forms, Qualtrics, etc.). When `url` is
empty the link is hidden.

## Parameters

- `heading` (optional): Heading text. Default: `"Share Your Feedback"`.
- `url` (optional): Full URL of the survey. When empty, the link element is hidden. Default: `""`.
- `url-label` (optional): Accessible link text. Default: `"feedback survey"`.
- `prompt` (optional): Prompt sentence below the heading. Default: standard text.

## Tags

feedback, closing, framing

## Usage

```markdown
---
id: feedback
use: catalog/feedback
params:
  url: "https://forms.example.edu/workshop-feedback"
  url-label: "workshop feedback form"
---
```
