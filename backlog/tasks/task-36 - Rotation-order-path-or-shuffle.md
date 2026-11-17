---
id: TASK-36
title: 'Rotation order: path or shuffle'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T11:51:00Z'
updated_date: '2026-11-17T11:53:00Z'
labels:
  - integration
milestone: m-3
dependencies: []
priority: medium
type: feature
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A setting on each rotation (its subentry flow): Order, either path order (default) or shuffle.

Shuffle works in rounds: every picture once per round in random order; a new round never starts with the picture just shown; pictures added mid-round join the round, deleted ones drop out. The position counts pictures shown this round. Switching back to path order continues from the current picture.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The rotation flow has Order (path order or shuffle), path order by default; changing it keeps the rotation's state
- [x] #2 Shuffle shows every picture once per round and never starts a round with the picture just shown
- [x] #3 Pictures added mid-round join the round; switching to path order continues from the current picture
- [x] #4 The image entity, diagnostics and the panel show the order; docs describe it
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
media.shuffle_next (no Home Assistant imports) picks the next picture of a round; the rotation state keeps the pictures shown in the round. Order is a subentry setting (path, default, or shuffle); the Next button passes it to Rotations.async_advance. The image entity attribute, diagnostics and the panel's rotation list show it. Tests check properties, so randomness cannot make them flaky. Checked in the Docker HA: reconfigured Living room to shuffle; two rounds each showed all five pictures once, the second starting with a different picture.
<!-- SECTION:NOTES:END -->
