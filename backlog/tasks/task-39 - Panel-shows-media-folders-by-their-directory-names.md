---
id: TASK-39
title: Panel shows media folders by their directory names
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:08:00Z'
updated_date: '2026-11-17T12:10:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: low
type: task
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Like Home Assistant's media browser, the panel shows each media folder by its directory's name (media, nas-photos) instead of its ID (local, nas). Paths in actions and patterns keep the IDs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Top level, breadcrumbs and the move dialog show directory names; paths keep the IDs
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Library.titles maps each media folder ID to its directory's name, as Home Assistant's local media source titles them (path.name). shoebox/browse returns the map and names top-level items by it; the panel shows the names in the breadcrumbs and the move dialog. The move dialog no longer offers the top level, which cannot hold files. Checked in the Docker HA: media and nas-photos at the top level, Media > nas-photos > Family, move targets media/... and nas-photos/....
<!-- SECTION:NOTES:END -->
