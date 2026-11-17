---
id: TASK-42
title: 'Image editor: transparent preview background'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:25:00Z'
updated_date: '2026-11-17T12:25:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: low
type: task
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The preview area keeps its constant height without a background: only the cropped picture shows.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The preview area is transparent; only the picture shows
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed the canvas background and border radius; height stays 160 px. Checked in the Docker HA.
<!-- SECTION:NOTES:END -->
