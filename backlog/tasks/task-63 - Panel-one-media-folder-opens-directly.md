---
id: TASK-63
title: 'Panel: one media folder opens directly'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T16:06:00Z'
updated_date: '2026-11-17T16:06:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: feature
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
With only one media folder chosen, the panel's top level showed a single tile. Open that folder directly, as Home Assistant's media browser does.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 With one chosen folder, /shoebox shows its contents; Media in the breadcrumbs stands for it; upload and new folder work there
- [x] #2 Links into the folder (/shoebox/folder/local/...) keep working; paths in actions and patterns do not change
- [x] #3 With two or more folders, the top level lists them as before
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Panel only: every browse and search returns the chosen folders (titles); with one, the route '' maps to it, links to it go to /shoebox, the breadcrumbs skip its step, and _shown names it Media. Checked in the dev HA by switching the options between local and local+nas: top level, opening a folder, back to Media, an old /shoebox/folder/local/... link, and back to two folders.
<!-- SECTION:NOTES:END -->
