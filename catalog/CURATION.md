# Catalog Curation Rules

The slide catalog (`catalog/`) holds finished, vetted, optionally parameterized
slides that are used across many decks. Two kinds belong here: framing slides
(opening, closing, legal/administrative and structural slides that are the
same regardless of topic) and program slides (standard slides for a program
such as CloudBank, reused across that program's talks).

## What belongs in the catalog

- **Framing slides** that appear in virtually every UW training deck: title,
  land acknowledgement, funding credit, agenda, feedback, closing.
- **Program slides** that a program presents the same way in most of its
  talks, such as CloudBank's eligibility and recommended uses. They carry the
  program's brand (`brand: cloudbank`, never `any`) and an ID prefix for that
  program (`cb-`), so they sort together and the planner only offers them to
  that program's decks.
- Slides where the wording has been reviewed and approved (land acknowledgement,
  funding, disclaimer language, program policy).
- Slides that would otherwise be rebuilt from scratch for every deck.

## What does not belong

- Topic-specific content slides that are not a program's standard slides:
  those belong in individual decks.
- Slides that are only useful in one training series or one talk.
- Slides that duplicate a layout: if the `title` layout template already
  handles a need, a catalog slide is not necessary.

## Catalog slide structure

Each slide lives in `catalog/slides/<id>/`:

```
catalog/slides/<id>/
├── slide.html    # HTML fragment with {{param}} placeholders
├── slide.md      # Metadata and documentation (front matter + body)
└── assets/       # Images or other files required by this slide only
```

`slide.md` front matter (restricted YAML subset):

| Field | Required | Meaning |
|-------|----------|---------|
| `id` | yes | Must equal the directory name |
| `description` | yes | One sentence; shown to the planner |
| `kind` | yes | `verbatim`, `parameterized`, or `derived` |
| `brand` | yes | `uw`, `cloudbank`, or `any` |
| `version` | yes | Semantic version (`"1.0.0"`) |
| `status` | yes | `draft`, `review`, or `ready` |
| `owner` | yes | Team or handle responsible for the slide |
| `params` | no | Map of param names to default values |

## Kinds

- **verbatim**: the HTML is used as-is; no `{{param}}` placeholders allowed.
- **parameterized**: the HTML contains `{{param}}` placeholders substituted
  by the resolver from the deck brief's `params:` map; defaults in `slide.md`.
- **derived**: the HTML contains `{{param}}` placeholders populated by the
  resolver's built-in generator (currently only `agenda`).

## Param substitution

Values are substituted with HTML escaping (`<`, `>`, `&`, `"`, `'`).
A missing param uses the default from `slide.md`'s `params:` map.
An empty string default means the element is typically empty or omitted.

## Versioning

- `catalog.yml` carries the catalog's own `version` string.
- Each slide's `slide.md` also carries a `version` (the slide's own revision,
  independent of the catalog version).
- Decks pin the catalog version in `deck.yml`'s `catalog:` field and in
  `.uw-slides.json`'s `catalog` field.
- A version pin of `null` means "use the catalog at the current plugin version."
- The resolver stamps `data-catalog="<slide-id>@<slide-version>"` on every
  resolved fragment.

## Eject

To stop tracking a catalog slide and treat it as a hand-edited local slide:

```bash
python3 tools/resolve-catalog.py eject . <slide-id>
```

This sets `locked: true` in the brief and removes `use:`. The existing
`content/<id>.html` is kept unchanged; future builds use it as a locked slide.
After ejecting, edit the brief and regenerate normally.

## Adding a new slide

1. Create `catalog/slides/<id>/slide.html` following the HTML conventions
   (scoped styles, brand tokens, `{{param}}` for substitution, minimum 1.5rem
   fonts, gold accent bar).
2. Create `catalog/slides/<id>/slide.md` with the required front matter.
3. Add the ID to `catalog/catalog.yml` under `slides:` and add a one-line
   description in the top-level key `<id>:`.
4. Review against `references/accessibility-requirements.md` and
   `design-systems/uw-brand/DESIGN.md`.
5. Set `status: ready` only after the content (especially any institutional
   wording) has been reviewed and approved.

## Size guideline

Keep the framing slides to about 10–15, and each program's slides to about
10–15 as well. The catalog is meant for slides that are reused nearly
unchanged, not a library of every possible layout.

## Program policy wording

Program slides often state policy that changes: eligibility, allocation sizes,
award numbers. Keep a program slide at `status: review` until its owner has
checked it against the program's current pages, list those pages in the
slide's `slide.md`, and bump the slide's `version` whenever the wording changes.

## Institutional wording

**Land acknowledgement and funding wording must never be invented.**
The placeholder text in the seeded slides is intentional. Replace it only with
text that has been reviewed and approved by the appropriate UW office.

- Land acknowledgement: contact the UW Office of Minority Affairs & Diversity
  (OMA&D) or the Office of the President for approved language.
- Funding credits: use the exact language required by the funding agency's
  award terms. Consult the UW Office of Sponsored Programs for guidance.
