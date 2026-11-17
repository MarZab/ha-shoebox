---
id: TASK-23
title: 'Panel: native look'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - panel
milestone: m-4
dependencies:
  - TASK-2
  - TASK-13
priority: high
type: task
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The panel uses HA frontend elements and theme variables. Every element and attribute it relies on exists in the pinned HA version and nothing private is used.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every ha-* element used exists in the pinned HA frontend and renders
- [ ] #2 Light and dark themes, narrow layout and the sidebar toggle work
- [ ] #3 No console errors while browsing, uploading, editing and viewing rotations
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
