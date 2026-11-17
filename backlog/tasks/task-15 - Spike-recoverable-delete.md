---
id: TASK-15
title: 'Spike: recoverable delete'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T11:27:00Z'
labels:
  - integration
milestone: m-2
dependencies: []
priority: low
type: spike
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decide whether deletes go to a hidden trash below /media, emptied after N days, or are final with the panel asking for confirmation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Outcome in docs/architecture.md; follow-up task if needed
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Home Assistant's media browser deletes local files permanently (local_source.async_delete_media unlinks the file) after a confirmation, with no trash; backups that include the media folder are the recovery. Shoebox does the same: final deletes, confirmation in the panel. Recorded in docs/architecture.md; actions.md and panel.md point to backups. No follow-up task.
<!-- SECTION:NOTES:END -->
