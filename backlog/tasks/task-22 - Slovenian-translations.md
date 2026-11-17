---
id: TASK-22
title: Slovenian translations
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-12
  - TASK-17
  - TASK-18
priority: low
type: task
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
translations/sl.json for config flow, options, subentry flow, actions, errors and entities, matching the Slovenian of the panel.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 sl.json has every key of en.json
- [ ] #2 A test fails when the keys of en.json and sl.json differ
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
