---
id: TASK-25
title: 'Panel: flows end to end'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - panel
milestone: m-4
dependencies:
  - TASK-23
  - TASK-16
priority: medium
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every panel flow works in the Docker HA with the sample media.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Upload by drop and picker, several at once, errors shown
- [ ] #2 Create folder, rename, move, delete with confirmation
- [ ] #3 Rotate and crop with every aspect option; the result matches the rendered picture
- [ ] #4 The rotations view lists rotations with thumbnail and match count and links to Settings to add, reconfigure and delete
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
