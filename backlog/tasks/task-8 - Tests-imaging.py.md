---
id: TASK-8
title: 'Tests: imaging.py'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 rotated() for all 8 orientations and 90, 180, 270, -90; other angles refused
- [ ] #2 set_orientation with and without EXIF; the bytes after SOS are unchanged
- [ ] #3 set_crop and get_crop round trip; other XMP fields kept; clearing removes only the crop
- [ ] #4 crop_shown and crop_as_shown are inverse for every orientation
- [ ] #5 render cover and contain: exact size, orientation and crop visible in pixels, baseline JPEG
- [ ] #6 Edits on PNG refused; damaged JPEG and damaged EXIF raise ImageError
- [ ] #7 Line coverage at least 90%
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
