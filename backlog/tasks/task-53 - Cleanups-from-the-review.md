---
id: TASK-53
title: Cleanups from the review
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - integration
  - panel
milestone: m-5
dependencies: []
priority: low
type: chore
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dead code (store migrate function, media.move, Variant.hit, unused panel properties and CSS), the loaded-entry lookup in one place, shared constants, the device view checking If-None-Match before rendering, and backlog ticket descriptions that later changes made out of date.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No dead code or duplicated lookups listed in the review remain
- [ ] #2 Done tickets' descriptions match the current design
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
