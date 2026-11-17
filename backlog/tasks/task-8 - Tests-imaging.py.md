---
id: TASK-8
title: 'Tests: imaging.py'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:58:00Z'
labels:
  - tests
milestone: m-1
dependencies:
  - TASK-6
priority: high
type: task
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Orientation arithmetic, EXIF and XMP rewriting, rendering.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 rotated() for all 8 orientations and 90, 180, 270, -90; other angles refused
- [x] #2 set_orientation with and without EXIF; the bytes after SOS are unchanged
- [x] #3 set_crop and get_crop round trip; other XMP fields kept; clearing removes only the crop
- [x] #4 crop_shown and crop_as_shown are inverse for every orientation
- [x] #5 render cover and contain: exact size, orientation and crop visible in pixels, baseline JPEG
- [x] #6 Edits on PNG refused; damaged JPEG and damaged EXIF raise ImageError
- [x] #7 Line coverage at least 90%
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
imaging.py ported fully typed; truncated JPEGs now raise ImageError instead of IndexError. Rotation is checked against Pillow's exif_transpose for all 8 orientations x 4 angles. 94% line coverage.
<!-- SECTION:NOTES:END -->
