---
id: TASK-53
title: Cleanups from the review
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T13:10:00Z'
labels:
  - integration
  - panel
milestone: m-5
dependencies: []
priority: low
type: chore
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dead code (store migrate function, media.move, Variant.hit, unused panel properties and CSS), the loaded-entry lookup in one place, shared constants, the device view checking If-None-Match before rendering, and backlog ticket descriptions that later changes made out of date.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No dead code or duplicated lookups listed in the review remain
- [x] #2 Done tickets' descriptions match the current design
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed: RotationStore (plain Store; core handles versions), media.move (moves go through Library; tests too), the panel's unused panel setter, redundant CSS, ha-menu-button from the element list, crop.js's box-changed event nobody listened to and its duplicate media-query rule; crop.js frees its object URL when it leaves the page. One place finds the loaded entry and its rotations (runtime.loaded_entry, loaded_shoebox, rotations_of), used by views, services, WebSocket and media source; the media view now checks the subentry type. One FRACTION schema. media_url uses MEDIA_URL's prefix. The device view answers If-None-Match from the cache key before preparing. Blank rotation names are refused. Done tickets 11, 12, 13, 23, 25, 27, 28, 35, 36 describe the current design. Kept: Variant.hit (the cache tests check hits through it) and media.matches (the pattern table tests it); VariantCache.evict scanning the cache directory per miss is fine at the sizes we target.
<!-- SECTION:NOTES:END -->
