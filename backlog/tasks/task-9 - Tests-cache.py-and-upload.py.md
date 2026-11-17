---
id: TASK-9
title: 'Tests: cache.py and upload.py'
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
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Variant cache and upload naming.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The cache key changes with file size, mtime, dimensions, fit and extra
- [ ] #2 get_or_make: a miss makes once; a hit touches mtime and does not make
- [ ] #3 evict removes least recently used first, never the one just made; clear removes only variant and temp files
- [ ] #4 path() refuses names that are not variants
- [ ] #5 safe_name: path parts, backslashes, control characters, leading dots, long names
- [ ] #6 check_type, free_name numbering, finish never replaces an existing file
- [ ] #7 Line coverage at least 95% for both modules
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
