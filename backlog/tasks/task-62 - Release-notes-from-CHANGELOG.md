---
id: TASK-62
title: Release notes from CHANGELOG
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T16:02:00Z'
updated_date: '2026-11-17T16:04:00Z'
labels:
  - release
  - tooling
milestone: m-6
dependencies: []
priority: low
type: task
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The v0.1.0 GitHub release shows only GitHub's generated 'Full Changelog' link. HACS shows the release notes when updating, so release.yaml should use the version's section of CHANGELOG.md as the release body.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 release.yaml publishes the version's CHANGELOG.md section as the release text
- [x] #2 A tag without a CHANGELOG section still releases, with GitHub's generated notes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tools/scripts/release_notes.py prints the version's section (to the next ## heading, blank runs squeezed); release.yaml passes it with --notes-file next to --generate-notes, or only --generate-notes without a section. Tested with a changelog table (stable, beta heading, missing). The v0.1.0 release text can be fixed by hand: gh release edit v0.1.0 --notes-file <(python3 tools/scripts/release_notes.py 0.1.0).
<!-- SECTION:NOTES:END -->
