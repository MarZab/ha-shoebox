---
id: TASK-7
title: 'Tests: media.py'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 resolve: relative, absolute below the root, '..', NUL, the path itself a symlink, a symlinked folder leading outside, the root refused unless allowed
- [ ] #2 walk and list_folder: hidden names and symlinks skipped, sort order, types
- [ ] #3 Patterns: *, **, **/, ?, [...] and [!...], re:, invalid regex, empty pattern
- [ ] #4 select by type; first_match falls through to the next pattern
- [ ] #5 advance: first, next, wrap, current file gone, empty list
- [ ] #6 create_folder, move (into itself, target exists), rename (invalid name, collision), delete file and folder
- [ ] #7 Line coverage at least 95%
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
