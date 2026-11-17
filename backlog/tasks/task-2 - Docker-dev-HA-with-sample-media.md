---
id: TASK-2
title: Docker dev HA with sample media
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - tooling
milestone: m-0
dependencies:
  - TASK-1
priority: high
type: chore
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A local Home Assistant for manual testing, on the same HA version as the tests.

- docker/compose.yaml and docker/Dockerfile.ha; config in docker/ha-config (gitignored)
- the integration bind-mounted read-only at /config/custom_components/shoebox
- a small committed sample media folder mounted at /media
- tasks: dev:up, dev:down, dev:logs, dev:restart, dev:build
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `mise run dev:up` starts HA on :8123 and Shoebox Media Manager can be added
- [ ] #2 Sample media covers JPEG with EXIF orientation, PNG, HEIC and nested folders
- [ ] #3 `mise run dev:restart` picks up integration edits without a rebuild
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
