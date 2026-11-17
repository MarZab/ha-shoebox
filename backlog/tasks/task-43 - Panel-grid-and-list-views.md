---
id: TASK-43
title: 'Panel: grid and list views'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:36:00Z'
updated_date: '2026-11-17T14:05:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: feature
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Offer a grid view (today's tiles) and a list view (rows with a small thumbnail, name, size and date), switched the way Home Assistant's media browser does it. The choice is remembered per browser.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Grid and list views can be switched, matching how Home Assistant's media browser offers them
- [x] #2 The list view shows thumbnail, name, size and modified date, with the same menus and actions as the grid
- [x] #3 The choice is remembered per browser; light, dark and phone layouts work
- [x] #4 docs/panel.md describes it
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
As Home Assistant 2026.10's media browser: Auto, Grid and List in the top bar's ⋮ menu, the current one highlighted. List rows: 40 px thumbnail or icon, name, size and date, the same ⋮ menu. Auto: grid when the folder has pictures, list otherwise. Remembered in localStorage (wrapped in try/catch). Checked in light, dark and at phone width.
<!-- SECTION:NOTES:END -->
