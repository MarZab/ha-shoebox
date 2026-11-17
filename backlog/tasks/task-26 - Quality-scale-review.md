---
id: TASK-26
title: Quality scale review
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:35:00Z'
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
- [x] #1 quality_scale.yaml lists every Bronze and Silver rule with its status
- [x] #2 Tasks exist for the open rules
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
All 20 Bronze and 10 Silver rules recorded. Fixed on the way: test-before-setup (setup retries with a translated reason when the media folder is missing) and parallel-updates (PARALLEL_UPDATES = 0 on both platforms). Exempt: polling, conditions, triggers, test-before-configure, entity-unavailable, log-when-unavailable, reauthentication. The six open rules are documentation; TASK-27 and TASK-28 cover them (TASK-28 got criteria for configuration, installation parameters and removal).
<!-- SECTION:NOTES:END -->
