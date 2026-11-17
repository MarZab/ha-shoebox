---
id: TASK-41
title: 'Image editor: aspect ratio dropdown, capped preview'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:16:00Z'
updated_date: '2026-11-17T12:17:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: low
type: task
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The editor's aspect ratio becomes a dropdown (Home Assistant's ha-dropdown) showing the current ratio, instead of a row of buttons.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Aspect ratio is a dropdown showing the chosen ratio; choosing applies it to the crop box
- [x] #2 The preview area has a constant height (160 px, 120 px on phones); the picture fits inside it
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Aspect ratio is an ha-dropdown whose trigger shows the chosen ratio; choosing applies it to the crop box. The preview canvas is a constant 160 px high (120 px on phones), full width of its column, with object-fit: contain. Checked in the Docker HA: 9:16 gives a 0.5625 box; the preview stays 160 px high for free, 9:16 and 16:9.
<!-- SECTION:NOTES:END -->
