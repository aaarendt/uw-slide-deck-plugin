---
id: cb-title
description: "Standard CloudBank title slide with the CloudBank and NSF logos, NSF award numbers, presenter info and a partner logo band"
kind: parameterized
brand: cloudbank
version: "1.1.0"
in_agenda: false
owner: aaarendt
params:
  title: "Presentation Title"
  subtitle: ""
  presenter: ""
  affiliation: ""
  date: ""
---

# Description

Standard opening title slide for CloudBank decks, with the logos and award
credit NSF requires. On a white background with the Signal Blue accent bar:

- the CloudBank logo and the NSF logo, with "NSF Awards: 1925001 & 2505560"
  under the NSF logo;
- the title and subtitle in the centre;
- presenter, affiliation and date below;
- a Deep Navy band along the bottom with white logos of the CloudBank partners:
  San Diego Supercomputer Center, UC San Diego, University of Washington,
  UC Berkeley and Strategic Blue.

The logos and the award line are fixed, not params, so a deck cannot drop
them. It takes the same params as `uw-title`.

## Parameters

- `title` (required): Main presentation title shown large. Default: `"Presentation Title"`. Long titles wrap to up to four lines.
- `subtitle` (optional): Shown below the title in muted text. Default: `""` (hidden when empty).
- `presenter` (optional): Presenter name or names, for example `"Jane Doe, John Roe"`. Default: `""` (hidden when empty).
- `affiliation` (optional): Presenter's affiliation. Default: `""` (hidden when empty; the CloudBank logo is already on the slide).
- `date` (optional): Date string; quote dates in the brief. Default: `""` (hidden when empty).

## Assets

`assets/` holds the logo files. The resolver copies them into the deck at
`assets/images/catalog-cb-title/`, and `publish.sh` embeds them in the
published file.

| File | Source |
|------|--------|
| `cloudbank.png` | CloudBank logo, full colour, transparent background |
| `nsf.png` | NSF official logo (RGB EPS), rendered to a 600 px transparent PNG; the EPS converts to a 13 MB SVG, so PNG is used |
| `sdsc-white.svg` | SDSC logo (SVG), recoloured white |
| `ucsd-white.svg` | UC San Diego logo (SVG), recoloured white |
| `uw-white.svg` | UW stacked wordmark (EPS), converted to SVG and recoloured white |
| `berkeley-white.svg` | UC Berkeley logo (PNG), traced to SVG in white |
| `strategic-blue-white.svg` | Strategic Blue logo (PNG), traced to SVG in white |

Use official logo files only. When a partner, award number or logo changes,
replace the file or the award line here and bump `version`; every deck picks
it up on its next resolve. If an organisation supplies an official white
(reversed) logo, prefer it to the recoloured or traced version.

Accepted by the slide owner on 2026-11-03. The award line uses the award
numbers supplied by the slide owner.

## Accessibility

Each logo has alt text naming the organisation; the partner band is a list
labelled "CloudBank partners". The logos are a required credit, not
decoration, so screen readers announce them.

## Tags

title, cloudbank, framing, opening, nsf, logos, partners

## Usage

In a deck brief:

```markdown
---
id: title
use: catalog/cb-title
params:
  title: "CloudBank for Researchers"
  subtitle: "Cloud access for NSF-funded research"
  presenter: "Jane Doe"
  date: "November 3, 2026"
---
```
