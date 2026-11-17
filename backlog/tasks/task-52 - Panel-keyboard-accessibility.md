---
id: TASK-52
title: Panel keyboard accessibility
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: task
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tiles, breadcrumbs and move-dialog rows are reachable and usable with the keyboard (focus, Enter/Space, labels); the crop box can be moved and resized with arrow keys; Escape in the editor goes back to the viewer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every action in the panel is reachable by keyboard
- [ ] #2 The crop box moves and resizes with arrow keys
- [ ] #3 Escape in the editor returns to the viewer
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
