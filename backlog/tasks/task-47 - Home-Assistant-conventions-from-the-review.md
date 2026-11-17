---
id: TASK-47
title: Home Assistant conventions from the review
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - integration
milestone: m-5
dependencies: []
priority: medium
type: task
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
- a chosen folder missing from media_dirs is a configuration error (ConfigEntryError / repair), not an endless retry; a missing directory still retries
- WebSocket commands use core's error handling (translation key and placeholders), not a custom wrapper
- translations for the subentry reconfigure abort
- quality_scale.yaml reviewed against these
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Unconfigured folder: setup error without retries; missing directory: retry
- [ ] #2 WebSocket errors carry translation_key and placeholders
- [ ] #3 reconfigure_successful is translated; hassfest passes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
