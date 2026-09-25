# [Presentation Name]

Built with the `uw-slides` plugin.

Before writing any slide HTML, read:
- `~/.claude/plugins/local/uw-slides/CLAUDE.md` — architecture, build workflow, skill list
- `~/.claude/plugins/local/uw-slides/design-systems/[BRAND]-brand/DESIGN.md` — colors, type, spacing, patterns
- `~/.claude/plugins/local/uw-slides/references/accessibility-requirements.md`

## After every edit batch

```
/uw-slides:design-review
/uw-slides:accessibility-check
```

## Build

```bash
./build.sh              # pass 1 → build/index.html
./build-visuals.sh      # pass 2 → build/index-with-visuals.html
./publish.sh            # pass 3 → build/index-published.html (self-contained)
```
