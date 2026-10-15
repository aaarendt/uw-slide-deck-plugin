## Slides changed

<!-- List the slide IDs added, modified, or removed. Example:
- Added: 05-results (new data slide)
- Updated brief: 03-overview (key message revised)
- Regenerated: 03-overview (brief changed)
- Locked: 07-custom-diagram (hand-edited HTML)
-->

## Objective coverage

<!-- Which learning objective does this change serve?
Copy the relevant objective ID(s) from deck.yml. -->

## Preview

<!-- Link to the CI artifact (Actions → this run → Artifacts → deck).
If CI has not run yet, note "preview pending". -->

## Checklist

- [ ] Lint passes: `python3 tools/lint.py .` (or wait for CI)
- [ ] Every changed slide has a brief in `slides/<id>.md`
- [ ] Generated fragments committed on this branch (not regenerated on main)
- [ ] Any locked slides documented with a reason in the brief's `## Notes`
- [ ] Images have alt text; sources credited in the brief `## Notes`
- [ ] Font sizes meet the minimum (`clamp(1.5rem, …)`); run `python3 tools/lint.py .` to verify
