---
id: TASK-7
title: 'Tests: media.py'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:56:00Z'
labels:
  - tests
milestone: m-1
dependencies:
  - TASK-6
priority: high
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Path confinement, listing, patterns, rotation order and file operations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 resolve: relative, absolute below the root, '..', NUL, the path itself a symlink, a symlinked folder leading outside, the root refused unless allowed
- [x] #2 walk and list_folder: hidden names and symlinks skipped, sort order, types
- [x] #3 Patterns: *, **, **/, ?, [...] and [!...], re:, invalid regex, empty pattern
- [x] #4 select by type; first_match falls through to the next pattern
- [x] #5 advance: first, next, wrap, current file gone, empty list
- [x] #6 create_folder, move (into itself, target exists), rename (invalid name, collision), delete file and folder
- [x] #7 Line coverage at least 95%
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
media.py ported fully typed; 99% line coverage (the uncovered lines handle a file vanishing between listing and stat).
<!-- SECTION:NOTES:END -->
