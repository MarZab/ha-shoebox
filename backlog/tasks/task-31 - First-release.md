---
id: TASK-31
title: First release
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - release
milestone: m-6
dependencies:
  - TASK-4
  - TASK-5
  - TASK-25
  - TASK-26
  - TASK-27
  - TASK-28
  - TASK-30
priority: high
type: task
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tag the first release and install it through HACS as a custom repository on a clean Docker HA.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CHANGELOG has the version's entry
- [ ] #2 The tag matches manifest.json and release.yaml creates the GitHub release
- [ ] #3 Installed through HACS on a clean HA: integration, rotations, actions, entities, device URL and panel work
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
