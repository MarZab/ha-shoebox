---
id: TASK-60
title: 'Brand icon: a shoebox'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T15:04:00Z'
updated_date: '2026-11-17T15:07:00Z'
labels:
  - release
milestone: m-6
dependencies: []
priority: medium
type: task
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The brand icon (HACS, Settings) looked like a bucket: tall, tapered, no lid. Redrawn as a low, wide shoebox with its lid off behind it and two photos inside. The sidebar keeps mdi:image-album.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 brand/icon.png and icon@2x.png show the shoebox, drawn by tools/scripts/brand_icon.py
- [x] #2 The sidebar icon stays mdi:image-album
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Chosen by the user from a draft. Checked on the integration page in the dev HA, where Settings trims the transparent edges.

docs/images/settings.png retaken with the new icon (960 x 600 at 2x).
<!-- SECTION:NOTES:END -->
