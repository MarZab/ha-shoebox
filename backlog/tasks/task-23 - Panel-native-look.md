---
id: TASK-23
title: 'Panel: native look'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:30:00Z'
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
- [x] #1 Every ha-* element used exists in the pinned HA frontend and renders
- [x] #2 Light and dark themes, narrow layout and the sidebar toggle work
- [x] #3 No console errors while browsing, uploading, editing and viewing rotations
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
All 13 ha-* elements the panel uses are defined in the frontend of Home Assistant 2026.10.4 and render; light and dark follow the theme, the phone layout shows the sidebar menu button, no console errors while browsing, in the picture viewer and on the rotations view. mise run dev:panel repeats the check headless (tools/scripts/panel_check.js) and saves screenshots to docker/screenshots. The rotations view still shows the old rotation fields (no names, image.undefined): TASK-25.
<!-- SECTION:NOTES:END -->
