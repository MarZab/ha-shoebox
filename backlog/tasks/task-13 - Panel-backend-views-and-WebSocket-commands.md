---
id: TASK-13
title: 'Panel backend: views and WebSocket commands'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:19:00Z'
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
- [x] #1 Render view: admin only, size and fit validated, path confined, crop=0 honoured
- [x] #2 Upload view: admin only, type check, size limit, missing part, free name on collision, temp file removed on failure
- [x] #3 Admin-only views use homeassistant.components.http.require_admin
- [x] #4 The upload size limit is the integration's own documented constant
- [x] #5 Concurrent renders are capped so a folder of thumbnails cannot exhaust CPU or memory
- [x] #6 Each WebSocket command: result shape, admin only, refusal returned as an error
- [x] #7 The panel is registered for admins only, only while Show in sidebar is on, and removed on unload
- [x] #8 The panel opens as Shoebox in the Docker HA sidebar
- [x] #9 Switching Show in sidebar adds or removes the panel without a restart
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
views.py (render, upload), websocket.py (browse, folders, info, edit, rotations, match), panel.py (static files under a content hash, panel_custom registration). The panel is registered per entry while Show in sidebar is on; OptionsFlowWithReload makes the toggle apply without a restart. Shoebox.picture caps concurrent renders (CONCURRENT_RENDERS=2) and returns bytes whether the cache is on or off. Upload limit MAX_UPLOAD_BYTES=200 MB; non-multipart bodies get 400. Home Assistant's security filter answers '../' in a query with 400 before the view runs. Dev dependency home-assistant-frontend==20260930.5 (what HA 2026.10.4's frontend requires) lets the tests load the panel. mypy: implicit_reexport for homeassistant.*. Frontend files ported as they are; its rotation editor still calls rotation actions that no longer exist: TASK-25. Verified in the Docker HA: panel Shoebox (admin, mdi:image-album), module served, browse and signed thumbnails work.
<!-- SECTION:NOTES:END -->
