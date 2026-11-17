---
id: TASK-9
title: 'Tests: cache.py and upload.py'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:59:00Z'
labels:
  - tests
milestone: m-1
dependencies:
  - TASK-6
priority: high
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Variant cache and upload naming.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The cache key changes with file size, mtime, dimensions, fit and extra
- [x] #2 get_or_make: a miss makes once; a hit touches mtime and does not make
- [x] #3 evict removes least recently used first, never the one just made; clear removes only variant and temp files
- [x] #4 path() refuses names that are not variants
- [x] #5 safe_name: path parts, backslashes, control characters, leading dots, long names
- [x] #6 check_type, free_name numbering, finish never replaces an existing file
- [x] #7 Line coverage at least 95% for both modules
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
cache.py and upload.py ported fully typed. Coverage: cache.py 100%, upload.py 98% (the uncovered line is running out of free names after 10000 tries).
<!-- SECTION:NOTES:END -->
