---
id: TASK-21
title: Diagnostics
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:27:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-16
priority: low
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
diagnostics.py for the config entry: options, cache usage, and per rotation its patterns, count and position. No file contents.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Download diagnostics works and is tested
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Options, cache usage and limit, and per rotation its patterns, the pattern in use, position, count and last step. No file names: a test makes sure a picture's name does not appear.
<!-- SECTION:NOTES:END -->
