---
id: TASK-46
title: File handling robustness
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - integration
milestone: m-5
dependencies: []
priority: high
type: bug
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review.

- file names that are not valid UTF-8 no longer break listing, list, the media source or rotation state
- moving, renaming or deleting a rotation's current picture updates the rotation
- a reload or removal during a Next press cannot lose state or recreate the store file
- errors from decoding pictures become translated errors; file errors do not show host paths
- upload names are limited by bytes, not characters
- move and rename never replace a file that appears meanwhile
- a failed crop does not leave a half-applied edit
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Non-UTF-8 names are skipped from listings with one log line, and nothing fails
- [ ] #2 Rotations follow move and rename of their current picture and drop it on delete
- [ ] #3 Unload waits for a running Next press; removal leaves no store file
- [ ] #4 Picture decoding errors are translated; no error shown to a user contains a host path
- [ ] #5 Long non-ASCII upload names are shortened to fit 255 bytes
- [ ] #6 Move and rename refuse an existing target atomically; edits are all or nothing
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
