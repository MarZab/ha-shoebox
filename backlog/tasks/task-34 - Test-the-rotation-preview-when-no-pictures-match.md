---
id: TASK-34
title: Test the rotation preview when no pictures match
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T11:25:00Z'
updated_date: '2026-11-17T11:25:00Z'
labels:
  - tests
milestone: m-5
dependencies: []
priority: low
type: task
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The rotation flow's preview step when the patterns select nothing: it shows 0 and still lets the rotation be saved.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Preview with no matches shows count 0 and the rotation can be saved
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->
