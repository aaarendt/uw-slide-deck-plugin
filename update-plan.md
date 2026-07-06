# Plugin Update Plan: Two-Pass Slide Build with Visuals Layer

This plan describes an update to my slide-generation plugin to support a two-pass build workflow with a new visuals layer. It is written as a working brief for Claude Code in a separate chat session.

## Context

The plugin currently reads a single `SLIDES.md` file and generates per-slide HTML, then runs a stitching script that assembles the slides into a final `index.html`.

I'm moving to a two-pass workflow:

- **Pass 1 — content and structure.** Generate slides from `SLIDES.md` as today, but explicitly *without* photographs or decorative icons. The deck should look intentional and finished on its own using only typography, layout, color palette, and the gold accent. The goal is that I can present the deck after pass 1 alone if I had to — it should look complete, not naked.
- **Pass 2 — visual additions.** A new file, `VISUALS.md`, specifies photographs, diagrammatic accents, and icons to **add** to the already-rendered slides. Pass 2 modifies existing HTML rather than regenerating slides from scratch.

The reason for the separation is editorial, not technical. Pass 1 produces an unadorned deck I can rehearse with. Issues found in rehearsal go back into `SLIDES.md` and pass 1 rebuilds. Pass 2 runs only when content is settled. I want the workflow to enforce that rhythm — a single-command "do everything" mode would collapse the rehearsal pause that's the whole point.

## Files involved

- **`SLIDES.md`** — existing file. Now contains a "Two-pass workflow" instructions block at the top of its "How to render this deck" section. Read this for pass 1.
- **`VISUALS.md`** — new file. Read this for pass 2. Uses the same slide identifiers as `SLIDES.md` (`## 01-title`, `## 02-opening`, etc.) as anchors. Opens with a global-styling section that specifies the visual language for all diagrammatic elements and photographs. Per-slide entries describe *additions only*.

Both files should be co-located with the plugin invocation, the way `SLIDES.md` is today.

## Plugin changes needed

### 1. A new command for pass 2

Keep the existing build command unchanged — it should continue to build from `SLIDES.md` as it does today. Add a second command (suggested name: `build-visuals` or `apply-visuals`) that:

- Reads `VISUALS.md`.
- For each slide identifier listed there, modifies the existing per-slide HTML to add the specified visual elements.
- Skips slides that `VISUALS.md` explicitly marks "No additions" (slides 01, 02, 10 in the current draft).
- Skips slides not mentioned in `VISUALS.md` at all (treats absence as no change).
- Does **not** regenerate slides from `SLIDES.md` during this pass.

The two commands remain independent. Pass 2 is invoked deliberately, after rehearsal; it's not chained into pass 1.

### 2. The critical behavior — additive, not regenerative

This is the single biggest implementation risk and is worth handling early.

Many slide-generation flows, when asked to "modify existing HTML," will quietly regenerate the whole slide from source because diff-and-patch is harder. If the plugin does this, the two-pass workflow collapses into one — pass 2 just re-renders from `SLIDES.md` + `VISUALS.md` combined, losing any first-pass refinements that exist only in the rendered HTML.

There are three feasible implementations, in rough order of preference:

- **Option A — modify in place.** Parse the existing per-slide HTML, locate the appropriate insertion points, add the visual elements, re-serialize. Cleanest behavior; hardest to implement without regressions.
- **Option B — freeze and layer.** Save first-pass per-slide HTML to a stable artifact location (per-slide files or a snapshot directory). Pass 2 treats those frozen files as the source of truth and layers additions on top. Simpler to implement reliably; the first-pass output becomes an explicit artifact rather than an intermediate.
- **Option C — combined regenerate (fallback).** Pass 2 feeds both `SLIDES.md` and `VISUALS.md` to the generator and re-renders. I accept that hand-edits to first-pass HTML won't survive. Acceptable only if A and B both prove infeasible without major refactor — and please tell me explicitly if we land here so I know what to expect.

I'd rather know upfront which of these the plugin can support than discover the limitation after losing work.

### 3. Slide-identifier matching

Both files use identifiers like `## 01-title`, `## 02-opening`, etc. The pass 2 command needs to parse these from `VISUALS.md` and locate the corresponding rendered slide HTML. Matching should be exact and case-sensitive — no fuzzy matching, no positional fallbacks.

## Things to check in the existing plugin before changing anything

Please surface answers to these before making code changes, so we choose the implementation path deliberately rather than discovering constraints mid-build:

1. **How does the current plugin produce per-slide HTML?** Are slides written to separate files, held in memory and stitched at the end, or some other arrangement? This determines whether pass 2 has stable artifacts to modify.
2. **Where does per-slide HTML live between generation and final `index.html` assembly?** If it's purely in-memory, Option B may require introducing a new on-disk artifact.
3. **Is there an existing facility to "edit" a slide after generation, or does each invocation rebuild from scratch?** This is the Option A feasibility check in concrete terms.
4. **How does the plugin currently parse `SLIDES.md`?** Is the parser reusable for `VISUALS.md`, or does `VISUALS.md` need its own parsing logic? The two files have similar but not identical structures (`VISUALS.md` has a global styling section at the top before any slide blocks).

## Acceptance criteria

The update is complete when:

1. The existing build command works exactly as before, given the updated `SLIDES.md`.
2. A new command reads `VISUALS.md` and produces a final deck with the visual additions applied to the appropriate slides.
3. Running the new command when `VISUALS.md` is absent or empty does not break the existing build output.
4. Running the new command twice in succession produces the same output the second time as the first (idempotency — a sanity check that additions aren't being duplicated).
5. The plugin's behavior when pass 1 is re-run after pass 2 has already been applied is either preserved-and-correct, or documented clearly enough that I know what to expect.

## Out of scope for this update

- Changes to the *content* of `SLIDES.md` or `VISUALS.md`. Those are settled separately.
- A combined "build everything" command. Deliberately not wanted — the workflow's rhythm depends on the two passes being separate.
- Image curation, asset storage, or photo file management. `VISUALS.md` describes what each visual element should *do*; specific image files are provided separately.

## What to bring into the Claude Code session

When working with Claude Code on this update, share three things alongside this plan:

- The current plugin code.
- `SLIDES.md` (so the existing parser's expected input format is visible).
- `VISUALS.md` (so the new parser knows what structure to expect).