---
id: cb-getting-help
description: "Where to get help with CloudBank: video tutorials and the CloudBank Catalog, monthly office hours and the community forum, and help@cloudbank.org"
kind: parameterized
brand: cloudbank
version: "1.0.0"
owner: aaarendt
params:
  next-office-hours: ""
---

# Description

A "Learning and support" slide for the end of a CloudBank talk, after the
how-to-apply slides (`cb-process`, `cb-nairr`) and before `thank-you`. It
answers the "I don't have time to learn all this" quote on
`cb-what-weve-heard`.

The help is ordered by how people look for it. The left column, "Learn on your
own", has the video tutorials (Cloud 101 and the Cloud Clinics) and the
CloudBank Catalog. The right column, "Ask a person", has the monthly office
hours and the community forum. A shaded band at the bottom gives
help@cloudbank.org. Every item shows its web address, so the audience can act
on the slide; the icons are original line icons (inline SVG, decorative,
`aria-hidden`) in the style of `cb-why-cloud`.

Office hours have no address on the slide: each session has its own page on
cloudbank.org and there is no stable public list of upcoming sessions. Use the
`next-office-hours` param to show the next date for your talk.

The slide does not count the clouds. The CloudBank Catalog lists five (AWS,
Google Cloud, Microsoft Azure, IBM Cloud, Oracle Cloud Infrastructure), while
`cb-what-is`, `cb-why-choose` and the ACCESS resource pages list four. Settle
the number before adding it here.

## Parameters

- `next-office-hours` (optional): One line under the office hours item with the
  next session, for example `"Next: Wednesday, November 18"`. Check the date on
  cloudbank.org before the talk. Default: `""` (hidden when empty).

## Tags

cloudbank, help, support, office-hours, training, videos, forum, contact, closing

## Sources

Content proposed by the slide owner on 2026-11-03, with the addresses supplied
by the owner and checked against these pages on 2026-11-03.

- Video tutorials page: Cloud 101 (6 videos) and Cloud Clinics: Deep Dives
  (12 videos), all on YouTube. "About every month" for new Cloud Clinics: from
  the slide owner; the page gives no dates.
- CloudBank Catalog: compares compute, storage, network, database and big data
  services across the clouds offered through CloudBank.
- Office hours: the October 21, 2026 session page (10:00 to 11:00 am Pacific,
  on Zoom, for newcomers and for current users with operational or technical
  issues, contact help@cloudbank.org). "Monthly": sessions on the ACCESS events
  calendar on June 17, July 15, August 19 and October 21, 2026.
- Community forum: a Discourse forum with categories for AWS, Azure, software
  and tools, and general cloud questions.

Bump `version` whenever the wording changes.

- CloudBank, "Video Tutorials": https://www.cloudbank.org/video-tutorials
- CloudBank, "CloudBank Catalog": https://www.cloudbank.org/cloudbank-catalog
- CloudBank, "CloudBank Office Hours: October 21, 10:00 - 11:00 AM Pacific": https://www.cloudbank.org/news/cloudbank-office-hours-october-21-1000-1100-am-pacific
- ACCESS events, "CloudBank Office Hours" (August 19, 2026): https://support.access-ci.org/events/9198
- CloudBank Community: https://community.cloudbank.org/

## Usage

```markdown
---
id: getting-help
use: catalog/cb-getting-help
params:
  next-office-hours: "Next: Wednesday, November 18"
---
```

To customise beyond `next-office-hours`, eject it and edit the HTML directly.

```bash
python3 tools/resolve-catalog.py eject . getting-help --catalog=<plugin>/catalog
```
