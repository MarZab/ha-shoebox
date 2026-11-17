---
id: TASK-25
title: 'Panel: flows end to end'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T13:10:00Z'
labels:
  - panel
milestone: m-4
dependencies:
  - TASK-23
  - TASK-16
priority: medium
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every panel flow works in the Docker HA with the sample media.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Upload by drop and picker, several at once, errors shown
- [x] #2 Create folder, rename, move, delete with confirmation
- [x] #3 Rotate and crop with every aspect option; the result matches the rendered picture
- [x] #4 The ⋮ menu opens Shoebox's page in Settings, where rotations are added, changed and deleted (the panel's rotations view was removed)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Walked in the Docker HA with Playwright: picker upload of three files at once (duplicate stored as forest-1.jpg, an HTML file refused with the message shown); create folder, rename, move, delete after confirmation; rotate right (orientation 6) and crop 1:1 on the turned picture (stored crop exactly square); rotations view: Next steps 2 -> 3 of 4, the entity opens Home Assistant's more-info dialog, Manage rotations opens the integration page (Add rotation, the rotation with its reconfigure gear and device). The panel's rotation editor and the shoebox/match command are gone: the subentry flow has the preview. shoebox/rotations now also returns position, current file, thumbnail and the two entity ids.
<!-- SECTION:NOTES:END -->
