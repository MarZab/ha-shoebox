---
id: TASK-19
title: Device image URL
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:25:00Z'
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
- [x] #1 Without a token 401; a non-admin user's token gets the picture
- [x] #2 Unknown or foreign entity 404; invalid size or fit 400
- [x] #3 Baseline JPEG at the requested size and fit
- [x] #4 304 while unchanged, 200 after the rotation advances
- [x] #5 The URL stays the same across advances, reloads and restarts
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
DeviceImageView at /api/shoebox/image/<entity_id>: width/height default to the entity size and fit to contain. ETag is the variant key (it changes with the file, its edits, the size and fit); Cache-Control no-cache so clients revalidate; Last-Modified from the rotation's last step. Only this integration's image entities. Verified in the Docker HA: 800x480 cover baseline JPEG with ETag and Last-Modified; If-None-Match gives 304.
<!-- SECTION:NOTES:END -->
