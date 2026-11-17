---
id: TASK-20
title: Media source
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-16
priority: medium
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A media_source platform: each rotation is a folder of its matching pictures in the media browser, playable on media players, prepared through the variant cache.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rotations browsable in the media browser
- [ ] #2 A picture plays on a media player
- [ ] #3 Tested with the media_source test helpers
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
