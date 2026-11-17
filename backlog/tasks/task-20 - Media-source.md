---
id: TASK-20
title: Media source
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:26:00Z'
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
- [x] #1 Rotations browsable in the media browser
- [x] #2 A picture plays on a media player
- [x] #3 Tested with the media_source test helpers
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
media_source.py: root lists rotations (thumbnail = current picture), each rotation lists the pictures it selects. Players get URLs that Home Assistant signs for its content user, who is not an admin, so MediaView (/api/shoebox/media/<rotation>/<path>) serves any user, but only pictures the rotation selects: 1920x1080 contain, or 320x320 cover with ?thumb=1. Home Assistant's own Image source already lists each rotation's image entity. Verified in the Docker HA: Shoebox listed among media sources, rotation browsable, resolved URL serves a JPEG.
<!-- SECTION:NOTES:END -->
