---
id: TASK-28
title: User documentation
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T13:10:00Z'
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
- [x] #1 docs/README.md indexes every page
- [x] #2 use-cases.md: a step-by-step recipe with YAML for each README use case
- [x] #3 actions.md: every action with fields, an example and the full response
- [x] #4 entities.md: devices, image and Next button entities, attributes, when they update
- [x] #5 displays.md: picture cards, notifications, media browser; the device URL with sizes, a dedicated non-admin user and token, and a complete ESPHome example refreshed when the rotation advances
- [x] #6 editing.md: rotate and crop as EXIF and XMP, which apps honour them, JPEG only, HEIC
- [x] #7 panel.md: browsing, upload, move, rename, delete, editor, rotations, Show in sidebar
- [x] #8 cache.md: what is cached, where, the size limit, excluded from backups, clearing
- [x] #9 troubleshooting.md: common errors and where to look in the logs
- [x] #10 quality_scale.yaml: the docs-* rules marked todo are done
- [x] #11 rotations.md: patterns (glob, **, re:, ! exclusions, combined), order, changing files
- [x] #12 docs/configuration.md: adding the integration (choosing media folders), every option with what it does, and removing the integration (what stays: media files; what goes: rotations, the cache)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
docs/: README (index), use-cases, configuration, rotations, entities, actions, displays, editing, panel, cache, troubleshooting, with screenshots from the dev HA in docs/images. tests/test_docs.py checks every relative link and heading anchor. Checked in the Docker HA: the slideshow automation and picture entity card, and the Sort phone pictures script (moved the file into a month folder). Removing the integration now deletes its rotation state and cache (async_remove_entry), as configuration.md says; media files stay. quality_scale.yaml: the docs rules are done.
<!-- SECTION:NOTES:END -->
