---
id: TASK-6
title: Test fixtures
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:54:00Z'
labels:
  - tests
milestone: m-1
dependencies:
  - TASK-1
priority: high
type: task
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Shared building blocks in tests/conftest.py for the HA-free modules:
- a media root on tmp_path, laid out from a short spec of files and folders
- an image factory: small JPEG or PNG with coloured quadrants, optional EXIF orientation, optional XMP crop
- a pixel helper that reads the colour at a fraction of an image, to assert orientation and crop
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Fixtures are small and named after what they give
- [x] #2 Images are generated in memory; no binary test assets
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/images.py: quadrant pictures (JPEG keeps EXIF orientation and XMP crop), colour_at reads the nearest quadrant colour. tests/conftest.py: media_root and tree fixtures.
<!-- SECTION:NOTES:END -->
