# Contributing to UW Slides

This guide covers two scenarios:

- **Deck collaboration** — you are working with others on a presentation built with this plugin. This is the common case: jump straight to [Collaborating on a Deck](#collaborating-on-a-deck).
- **Plugin development** — you are adding skills, fixing the build tooling, or editing the design system. See [Developing the Plugin](#developing-the-plugin).

---

## Prerequisites

Install these before cloning anything:

| Tool | Minimum | Notes |
|------|---------|-------|
| git | any recent | `git --version` |
| Python 3 | 3.8+ | `python3 --version`; stdlib only, no pip needed |
| A browser | any | For `open build/index.html` |
| Claude Code | latest | For `/uw-slides:*` skills. Not required to build, lint or view. |

Claude Code is required to _generate_ slides (it runs the LLM that fills the layout slots). If you are only reviewing, linting, or building an existing deck you do not need it.

---

## Collaborating on a Deck

### From clone to preview in 10 minutes

```bash
# 1. Clone the deck repo
git clone <deck-repo-url>
cd <deck-name>

# 2. Build (no install step needed)
./build.sh

# 3. Preview
open build/index.html        # macOS
xdg-open build/index.html    # Linux
```

That is all that is required to preview. Python 3 is needed if `tools/deckparse.py` is present (it validates `deck.yml` and generates `OUTLINE.md`); the build still works without it by reading the slide list directly.

### Lint before submitting changes

```bash
python3 tools/lint.py .
```

Lint checks every slide fragment against the brief, verifies CSS scoping, font sizes, alt text, and `data-slide` naming. It must pass before merging. See [lint output](#lint-output) for common messages.

### Publish a portable preview

```bash
./publish.sh
# → build/index-published.html (all images inlined as base64)
```

Share `build/index-published.html` as a pull-request preview artifact or email attachment.

---

## Roles: Who Edits What

The deck has three layers. Each has a clear owner:

| Layer | Files | Who edits it |
|-------|-------|-------------|
| **Brief** | `deck.yml`, `slides/<id>.md` | The slide owner (human) |
| **HTML fragment** | `content/<id>.html` | Claude Code (generated from the brief) |
| **Locked fragment** | `content/<id>.html` when `locked: true` | The slide owner (hand-edited) |

**Never hand-edit a generated fragment.** If the HTML needs to change, update the brief and regenerate. The one exception is a slide with `locked: true` in its brief — that HTML is yours to edit directly, and the generator will never overwrite it.

### Brief ownership

Each `slides/<id>.md` brief has an `owner:` field in its front matter. That person:

- Approves changes to the key message, talking points and notes
- Decides when the slide is `status: done`
- Is the only one who should push direct edits to that brief

Deck repos can enforce this with GitHub CODEOWNERS (see `.github/CODEOWNERS` in the deck repo).

---

## Branch and PR Workflow

```
main  ←  feature/add-closing-slide  (brief edits + regenerated HTML)
      ←  content/update-agenda       (brief edit only; regenerate in CI or locally)
      ←  fix/lint-errors
```

Rules:

1. **Never push directly to `main` on a shared deck.** Open a pull request.
2. **One purpose per branch.** Brief edits, slide additions, and visual-pass changes should each be separate PRs unless they are inseparable.
3. **Regenerate on your branch, not on main.** If you edit a brief, run `/uw-slides:generate-slides <id>` on your branch. The PR diff will include both the brief change and the updated fragment.
4. **Lint must pass.** The CI workflow runs `python3 tools/lint.py .` on every push and pull request. Fix any errors before asking for review.
5. **Review the HTML diff** in the PR. Even though it is generated, a reviewer should sanity-check the output once before approving.

### Stale slides

If a brief is edited but the HTML fragment is not regenerated, `lint.py` reports the slide as `stale`. Either regenerate it or add a comment in the PR explaining why the regeneration is deferred.

---

## How to Lock a Slide

Lock a slide when you want to hand-edit the HTML and prevent the generator from overwriting it:

1. Open `slides/<id>.md`.
2. Add `locked: true` to the front matter.
3. Commit the brief change.
4. Edit `content/<id>.html` directly.
5. Commit the HTML change.

To unlock, remove `locked: true` from the brief. The next `/uw-slides:generate-slides` will regenerate the fragment from the brief. The old hand-edited HTML is replaced — make sure you have committed it and that you intend to discard it.

---

## Recording Model and Prompt Context in Commits

When a commit was produced in part by an LLM, record the key context so a future collaborator (or your future self) can reproduce the reasoning:

```
feat(slides): add closing slide with call-to-action

Key message: "Register at uw.edu/training by Dec 1"
Layout: closing
Model: Claude Sonnet 4.6 (claude-sonnet-4-6)
Prompt context: generated from slides/closing.md brief; closing layout, UW brand

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Guidelines:

- Include the **model name and ID** (e.g. `claude-sonnet-4-6`). Model behavior varies across versions; this helps diagnose regressions.
- Mention the **skill or prompt** used (`/uw-slides:generate-slides`, `/uw-slides:plan-deck`, manual prompt).
- If you provided source material (a paper, a prior deck, a syllabus), name it in the commit so reviewers know where the content came from.
- Do not include the full prompt in the commit — keep it short. The brief (`slides/<id>.md`) already captures the intended content; the commit message captures the LLM context.

---

## License and Attribution

### Plugin code

The plugin is licensed under the **MIT License** (see `LICENSE`). You may use, modify, and distribute it freely.

### Encode Sans (UW brand font)

Encode Sans is licensed under the **SIL Open Font License 1.1** (OFL-1.1). Key terms:

- You may use, study, modify and redistribute the fonts freely.
- Modified versions must be distributed under the OFL-1.1 and must not use the reserved font name "Encode Sans".
- The fonts may not be sold on their own.

The OFL-1.1 is included with the font distribution (`design-systems/uw-brand/fonts/`). When redistributing a deck that contains the fonts in `assets/fonts/`, include the OFL license notice.

### Open Sans (UW and CloudBank body font)

Open Sans is licensed under the **Apache License 2.0**. It is loaded via Google Fonts CDN; no local copy is required or included.

### UW brand assets

The UW brand guidelines, color values and the header/footer template that embeds UW colors are provided for use in UW-affiliated presentations. The UW visual identity is a trademark of the University of Washington. Do not use the UW brand elements in materials that are not affiliated with or authorized by the University of Washington.

Contact UW Creative Communications & Marketing at `uwcc@uw.edu` if you are unsure whether your use is authorized.

### Images and diagrams in your deck

Any images you add to `assets/images/` or `assets/diagrams/` are your responsibility. When using third-party images:

- Record the **source URL, author, license, and any attribution requirement** in the brief's `## Notes` section.
- For Creative Commons licenses that require attribution, add a visible attribution line (use the source-line font size: `clamp(1rem, 1.1vw, 1.25rem)`) to the slide itself.
- Do not use images whose license does not permit the intended use (e.g., commercial presentations from a CC-NC image).

---

## Lint Output

Common messages and what to do:

| Message | Fix |
|---------|-----|
| `missing fragment: <id>` | Run `/uw-slides:generate-slides <id>` |
| `stale: <id> (brief hash mismatch)` | Run `/uw-slides:generate-slides <id>` |
| `font-size below minimum: <selector>` | Replace the fixed size with `clamp(1.5rem, <vw>, <max>)` |
| `img missing alt: <selector>` | Add an `alt` attribute to the `<img>` |
| `unscoped style in <id>` | Add `section[data-slide="<id>"]` prefix to each CSS rule |
| `duplicate id: <id>` | Remove or rename the duplicate entry in `deck.yml` |
| `orphan fragment: <file>` | Either add the ID to `deck.yml` or delete the fragment |

Run with `--strict` to fail on warnings as well as errors (used in CI by default):

```bash
python3 tools/lint.py --strict .
```

---

## Developing the Plugin

Plugin source lives in this repository. Skills are in `skills/<name>/SKILL.md`; build templates in `templates/`; design system docs in `design-systems/`; tools in `tools/`.

### Making a change

1. Fork or branch from `main`.
2. Edit the relevant `SKILL.md`, template, or tool.
3. Test with a throwaway deck in `/tmp`:
   ```bash
   # From the plugin repo
   export UW_SLIDES_HOME=$(pwd)
   # In a Claude Code session pointed at /tmp
   /uw-slides:new-deck test-deck
   ```
4. Run the tools tests:
   ```bash
   python3 tools/test_deckparse.py
   python3 tools/test_lint.py
   python3 tools/test_resolve_catalog.py
   ```
5. Open a PR with the change and test results.

### Adding a skill

1. Create `skills/<name>/SKILL.md` following the format of an existing skill.
2. Add the skill entry to `.claude-plugin/plugin.json`.
3. Document it in `README.md` (Skills table) and update `CHANGELOG.md`.

### Versioning

`plugin.json` carries the version. The release process is in `CHANGELOG.md`. Bump to a new minor version for new features; patch for fixes; major for breaking changes.
