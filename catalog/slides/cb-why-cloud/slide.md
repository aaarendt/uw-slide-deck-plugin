---
id: cb-why-cloud
description: "Why use the cloud for research: data access, on-demand scale, parallel runs, LLMs, shared environments, hosted services"
kind: parameterized
brand: cloudbank
version: "1.0.1"
owner: aaarendt
params:
  lead: ""
---

# Description

A general motivation slide for cloud computing in research, meant to come
before the CloudBank program slides (`cb-what-is`, `cb-why-choose`). Six
benefits in a two-column grid of short headed items, each with an original
line icon (inline SVG, decorative, `aria-hidden`) in a tinted circle, in the
same style as `cb-why-choose`. No logos and no copied artwork.

The six items: bring compute to the data, scale up on demand, run in parallel,
use and deploy LLMs, share reproducible environments, host research services.
The on-slide text is short to fit the 1.5rem minimum font size; the speaker
notes give a fuller explanation of each, with example services the presenter
can name (no provider names appear on the slide itself).

## Parameters

- `lead` (optional): One line shown under the heading to tie the slide to the
  talk, for example `"Commercial cloud computing can help with research like
  yours. With cloud you can:"`. Default: `""` (hidden when empty).

The heading "Why cloud?" is fixed so the generated agenda can use it. To change
it, set `title:` in the brief (agenda label) or eject the slide.

## Tags

cloudbank, why-cloud, motivation, benefits, gpu, llm, reproducibility, program

## Sources

Item list approved by the slide owner on 2026-11-02. This slide states general
cloud capabilities, not CloudBank program policy. The services named in the
speaker notes are examples; re-check them when the slide is revised and bump
`version` if the wording changes.

## Usage

```markdown
---
id: why-cloud
use: catalog/cb-why-cloud
params:
  lead: "Commercial cloud computing can help with research like yours. With cloud you can:"
---
```

To customise beyond `lead`, eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . why-cloud --catalog=<plugin>/catalog
```
