# Presentation Title

Brief description of your presentation.

Target audience: 
Duration: 

## How to render this deck (instructions for the slide generator)

**This document is a design brief, not slide copy.**

**Two-pass workflow.** This deck is built in two passes, and SLIDES.md governs only the first.

- **First pass (this file): content and structure only.** Build the deck to a publishable-looking, intentional state using only typography, layout, color palette, and the gold accent. Use no photographs and no decorative icons in this pass. The deck should look complete on its own — if it had to be presented tomorrow with no images, it should feel finished rather than naked.
- **Second pass (separate VISUALS.md): additive visual elements.** After the first pass is rendered and rehearsed, VISUALS.md specifies photographs, diagrammatic accents, and iconography to *add* to existing slides. The second pass modifies the already-rendered HTML; it does not rebuild slides from scratch.
- **Do not anticipate the second pass during the first.** If a slide feels visually sparse, the correct response is stronger typography or layout, not a placeholder.

**General rules:**

- The **Key message** line is the slide's headline — often the only substantial text shown, set in large type.
- **Bullets** are talking points the speaker will deliver aloud. Do not render them verbatim on the slide.
- **Note to self** lines are for the speaker only. Never render them on the slide.
- **Source** lines render as a small footer citation — never as a content bullet.
- Default to one anchoring element per slide: a phrase, a number, or a small structural composition. When in doubt, less text.
- Maintain visual continuity: consistent type scale, generous whitespace, and the gold accent from the title slide.

## 01-title

Title slide with UW branding.
- Presenter name
- Title/affiliation
- Date

## 02-example

Add your slide ideas here. Use any format that makes sense to you:
- Bullet points
- Prose descriptions
- Notes to yourself
- Key message: The one thing the audience should take away.

---

## Notes

To add a new slide:
1. Add a `## slide-id` heading in the order you want
2. Add your content notes under that heading
3. Ask your LLM to generate the slide based on SLIDES.md
4. Run `./build.sh` to build the presentation

To reorder slides:
1. Move the `## slide-id` headings around in this file
2. Run `./build.sh` to rebuild
