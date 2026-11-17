---
id: TASK-52
title: Panel keyboard accessibility
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T13:07:00Z'
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
- [x] #1 Every action in the panel is reachable by keyboard
- [x] #2 The crop box moves and resizes with arrow keys
- [x] #3 Escape in the editor returns to the viewer
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Tiles (role=button), breadcrumbs (role=link) and Move rows (role=option, aria-selected) are focusable with a visible focus ring; Enter/Space click them. The crop picture is focusable: arrows move the box, Shift+arrows resize (aspect kept); an aria label explains the keys. Escape in the editor returns to the picture. Move without a choice shows 'Choose a folder first.' Checked by keyboard with Playwright and dev:panel.
<!-- SECTION:NOTES:END -->
