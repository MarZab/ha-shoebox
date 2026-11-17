---
id: TASK-28
title: User documentation
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:35:00Z'
labels:
  - docs
milestone: m-5
dependencies:
  - TASK-27
priority: high
type: docs
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
One page per topic in docs/, each opening with what the reader can do with it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/README.md indexes every page
- [ ] #2 use-cases.md: a step-by-step recipe with YAML for each README use case
- [ ] #3 rotations.md: patterns (glob, **, re:, fallbacks), order and wrap, changing files
- [ ] #4 actions.md: every action with fields, an example and the full response
- [ ] #5 entities.md: devices, image and Next button entities, attributes, when they update
- [ ] #6 displays.md: picture cards, notifications, media browser; the device URL with sizes, a dedicated non-admin user and token, and a complete ESPHome example refreshed when the rotation advances
- [ ] #7 editing.md: rotate and crop as EXIF and XMP, which apps honour them, JPEG only, HEIC
- [ ] #8 panel.md: browsing, upload, move, rename, delete, editor, rotations, Show in sidebar
- [ ] #9 cache.md: what is cached, where, the size limit, excluded from backups, clearing
- [ ] #10 troubleshooting.md: common errors and where to look in the logs
- [ ] #11 docs/configuration.md: adding the integration (no questions asked), every option with what it does, and removing the integration (what stays: media files; what goes: rotations, the cache)
- [ ] #12 quality_scale.yaml: the docs-* rules marked todo are done
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
