---
id: TASK-45
title: Bound the work of preparing and selecting pictures
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T12:41:00Z'
labels:
  - integration
  - security
milestone: m-5
dependencies: []
priority: high
type: bug
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review: one crafted picture or request must not stall Home Assistant.

- XMP crop parsing: no regex that backtracks on long whitespace; cap the XMP size read; read only the head of a file for XMP
- pictures above a pixel limit are refused before decoding (decompression bombs)
- the media source view checks one path against the rotation instead of listing every folder per request
- the device URL accepts a small set of sizes, so arbitrary sizes cannot keep the renderer busy or flush the cache
- selecting and shuffling pictures run in the executor; shuffle is linear
- patterns: limit repeated ** and guard re: patterns against catastrophic backtracking
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A picture with 64 KB of whitespace in its XMP crop is handled in well under a second
- [ ] #2 Pictures above the pixel limit are refused with a translated error and no large allocation
- [ ] #3 The media source view does not walk the media folders per request
- [ ] #4 The device URL only renders documented sizes; other sizes are refused
- [ ] #5 No selection, shuffle or pattern matching runs in the event loop; shuffle over 20 000 pictures takes milliseconds
- [ ] #6 Patterns with excessive ** are refused; re: patterns cannot stall Home Assistant
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
