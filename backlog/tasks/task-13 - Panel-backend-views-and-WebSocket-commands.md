---
id: TASK-13
title: 'Panel backend: views and WebSocket commands'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:59:00Z'
labels:
  - integration
  - panel
milestone: m-2
dependencies:
  - TASK-11
priority: high
type: task
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
What the panel talks to: the render and upload views and the WebSocket commands browse, folders, info, edit, rotations and match. The panel's picture URLs are signed for its user.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Render view: admin only, size and fit validated, path confined, crop=0 honoured
- [ ] #2 Upload view: admin only, type check, size limit, missing part, free name on collision, temp file removed on failure
- [ ] #3 Admin-only views use homeassistant.components.http.require_admin
- [ ] #4 The upload size limit is the integration's own documented constant
- [ ] #5 Concurrent renders are capped so a folder of thumbnails cannot exhaust CPU or memory
- [ ] #6 Each WebSocket command: result shape, admin only, refusal returned as an error
- [ ] #7 The panel is registered for admins only, only while Show in sidebar is on, and removed on unload
- [ ] #8 The panel opens as Shoebox in the Docker HA sidebar
- [ ] #9 Switching Show in sidebar adds or removes the panel without a restart
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
