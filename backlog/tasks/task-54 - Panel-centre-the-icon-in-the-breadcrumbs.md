---
id: TASK-54
title: 'Panel: centre the icon in the breadcrumbs'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:46:00Z'
updated_date: '2026-11-17T12:46:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: low
type: bug
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The folder icon before Media sat on the text baseline instead of centred.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The icon is vertically centred with the text
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Breadcrumb links are inline-flex, centred, gap 4px; measured centred in the Docker HA.
<!-- SECTION:NOTES:END -->
