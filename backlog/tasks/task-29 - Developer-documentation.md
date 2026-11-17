---
id: TASK-29
title: Developer documentation
status: Done
assignee: []
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:43:00Z'
labels:
  - docs
  - tooling
milestone: m-5
dependencies:
  - TASK-2
priority: medium
type: docs
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
For contributors and agents; AGENTS.md links here.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 development.md: setup, mise tasks, Docker HA, sample media, manual panel checklist
- [x] #2 architecture.md: modules, how a rotation advances, the device URL, the panel, storage, cache key
- [x] #3 architecture.md: the design choices and their reasons: organiser first with extras opt-in by use, UI-only configuration, rotations as config subentries, a device with image and Next button per rotation, no rotation actions, the device URL with long-lived tokens, sized for hundreds of items
- [x] #4 security.md: path confinement, symlinks, admin boundaries, signed panel URLs, device URL and tokens, upload rules
- [x] #5 testing.md: layout, fixtures, what is tested where
- [x] #6 release.md: versioning, tags, HACS
- [x] #7 AGENTS.md links to these pages
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
docs/development.md (setup, tasks, local HA, sample media, panel check and checklist), architecture.md (modules, data flow, storage, cache key, design choices with reasons, open questions), security.md, testing.md, release.md. AGENTS.md now keeps the rules and links to these pages; the link test covers it.
<!-- SECTION:NOTES:END -->
