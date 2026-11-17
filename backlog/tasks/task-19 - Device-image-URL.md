---
id: TASK-19
title: Device image URL
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-17
priority: high
type: feature
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A stable URL per rotation for devices outside HA, such as ESPHome online_image with request_headers.

GET /api/shoebox/image/<entity_id>?width=&height=&fit=cover|contain
- authenticated with a Bearer long-lived token; any user, admin not required
- only this integration's image entities
- the current picture through the variant cache, baseline JPEG
- ETag and Last-Modified; 304 on a matching conditional request
- sizes 1..4096
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Without a token 401; a non-admin user's token gets the picture
- [ ] #2 Unknown or foreign entity 404; invalid size or fit 400
- [ ] #3 Baseline JPEG at the requested size and fit
- [ ] #4 304 while unchanged, 200 after the rotation advances
- [ ] #5 The URL stays the same across advances, reloads and restarts
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
