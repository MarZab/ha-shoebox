---
id: TASK-22
title: Slovenian translations
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:28:00Z'
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
- [x] #1 sl.json has every key of en.json
- [x] #2 A test fails when the keys of en.json and sl.json differ
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
translations/sl.json covers config flow, rotation subentries, options, the Next button, actions, selectors and errors, in the panel's vocabulary (rotacija, mapa z mediji, obreži). tests/test_definitions.py fails when the keys or placeholders of en.json and sl.json differ.
<!-- SECTION:NOTES:END -->
