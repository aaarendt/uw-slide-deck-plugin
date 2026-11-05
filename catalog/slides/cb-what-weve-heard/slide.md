---
id: cb-what-weve-heard
description: "The friction: four paraphrased researcher quotes about cloud access, moving work, platform setup and surprise bills"
kind: verbatim
brand: cloudbank
version: "1.0.0"
owner: aaarendt
---

# Description

A dark slide of four paraphrased researcher quotes in a row of cards, under the
eyebrow "The friction". It makes the problem human before the CloudBank program
slides answer it, so it fits between `cb-why-cloud` and `cb-what-is`. Each
quote maps to a later slide:

| Quote | Answered by |
|-------|-------------|
| No account without a university credit card | `cb-why-choose`: no card or purchase agreement |
| No time to learn it, need a jump start | `cb-getting-help`: video tutorials, office hours, forum and helpdesk |
| Setup different for every platform | `cb-why-choose`: one account, multiple clouds |
| Opaque $12K bill, no time to dig into it | `cb-why-choose`: cost monitoring and spending cap |

The quote marks and card borders use the CloudBank amber accent
(`--cb-accent-amber`, 6.3:1 on Deep Navy); they are decorative and
`aria-hidden`. The eyebrow and the source line use Mist (7.9:1). A source line
at the bottom says the quotes are paraphrased; keep it if you edit the quotes.

## Tags

cloudbank, friction, quotes, researchers, challenges, motivation, program

## Sources

Approved by the slide owner on 2026-11-02. The quotes are paraphrased from
conversations with researchers, not verbatim, and the slide says so.

## Usage

```markdown
---
id: what-weve-heard
use: catalog/cb-what-weve-heard
---
```

No parameters. This slide is verbatim: to use your own quotes, eject it and
edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . what-weve-heard --catalog=<plugin>/catalog
```
