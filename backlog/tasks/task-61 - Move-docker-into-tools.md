---
id: TASK-61
title: Move docker/ into tools/
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T15:05:00Z'
updated_date: '2026-11-17T15:05:00Z'
labels:
  - tooling
milestone: m-5
dependencies: []
priority: low
type: chore
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The local Home Assistant is developer tooling: docker/ moves to tools/docker/ (compose file; its configuration, media and screenshots stay out of Git).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 tools/docker/compose.yaml runs the dev Home Assistant with the same config, media and container
- [x] #2 Tasks, scripts, .gitignore and docs use tools/docker/
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Stopped the stack, moved the folder with its ignored contents, compose mounts ../../custom_components. The project name shoebox-dev keeps the same container. Checked: mounts, image.living_room keeps its state, dev:panel passes. Older tickets mention docker/ as history.
<!-- SECTION:NOTES:END -->
