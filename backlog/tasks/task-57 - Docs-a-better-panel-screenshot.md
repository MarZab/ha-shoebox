---
id: TASK-57
title: 'Docs: a better panel screenshot'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T14:46:00Z'
updated_date: '2026-11-17T14:46:00Z'
labels:
  - docs
milestone: m-5
dependencies: []
priority: medium
type: docs
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The README screenshot showed generated test pictures and a repair badge on Settings. Real photos, three thumbnails a row with the sidebar docked, sharp on high-density screens.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The README and panel.md screenshot shows real photos, three a row, the sidebar docked, no badges
- [x] #2 The photos can be fetched again with a script
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tools/scripts/screenshot_photos.py downloads six picsum (Unsplash licence) photos into Photos/Summer 2025. 960 x 690 at 2x (871-975 px keeps the sidebar docked and three columns), JPEG quality 88: 330 KB instead of 1.5 MB PNG. docs/images/panel.png replaced by panel.jpg.
<!-- SECTION:NOTES:END -->
