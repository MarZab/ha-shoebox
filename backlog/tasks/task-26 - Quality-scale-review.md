---
id: TASK-26
title: Quality scale review
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
  - docs
milestone: m-5
dependencies:
  - TASK-12
  - TASK-13
  - TASK-17
  - TASK-18
  - TASK-19
priority: medium
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
quality_scale.yaml with every Bronze and Silver rule of the integration quality scale marked done or exempt with a reason. Cheap gaps fixed; the rest become tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 quality_scale.yaml lists every Bronze and Silver rule with its status
- [ ] #2 Tasks exist for the open rules
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
