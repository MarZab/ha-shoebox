---
id: TASK-29
title: Developer documentation
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 development.md: setup, mise tasks, Docker HA, sample media, manual panel checklist
- [ ] #2 architecture.md: modules, how a rotation advances, the device URL, the panel, storage, cache key
- [ ] #3 architecture.md: the design choices and their reasons: organiser first with extras opt-in by use, UI-only configuration, rotations as config subentries, a device with image and Next button per rotation, no rotation actions, the device URL with long-lived tokens, sized for hundreds of items
- [ ] #4 security.md: path confinement, symlinks, admin boundaries, signed panel URLs, device URL and tokens, upload rules
- [ ] #5 testing.md: layout, fixtures, what is tested where
- [ ] #6 release.md: versioning, tags, HACS
- [ ] #7 AGENTS.md links to these pages
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
