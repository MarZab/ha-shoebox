---
id: TASK-18
title: Next button
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-17
priority: high
type: feature
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A button entity "Next" on each rotation device (has_entity_name, translation_key, unique_id from the subentry id). Pressing it advances the rotation. There is no action and no interval setting: timed advancing is an automation that presses the button, as HA recommends for user-chosen schedules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pressing Next advances the rotation and updates its image entity
- [ ] #2 The button is created and removed with its rotation
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
