## What this changes

<!-- One or two sentences. Name the skill, tool, template, or design-system file changed. -->

## Why

<!-- Link to the relevant workstream in plan.md, a GitHub issue, or give a brief rationale. -->

## Checklist

- [ ] Tests pass: `python3 tools/test_deckparse.py && python3 tools/test_lint.py && python3 tools/test_resolve_catalog.py && python3 tools/test_validate_plugin.py`
- [ ] Packaging valid: `python3 tools/validate_plugin.py`
- [ ] CLAUDE.md and README.md updated if the change affects skill behaviour, paths, or the user-facing workflow
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] `plan.md` progress checklist updated if this completes a workstream task
- [ ] No new hard-coded `~/.claude/plugins/local/uw-slides` paths (skills use `<PLUGIN>/...` and their "Plugin directory" section)
- [ ] Any new HTML fragments follow the font-size rules (`clamp(1.5rem, …)`, source lines excepted)
