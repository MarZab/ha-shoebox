---
id: TASK-16
title: Rotations as config subentries
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:21:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-11
priority: high
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Each rotation is a config subentry of the Shoebox entry, managed under the integration in Settings. The subentry id is its identity and the title only a label, so renaming keeps its entity.

- subentry flow `rotation`: name and patterns (multi-value text), a preview step with the match count and first matches, reconfigure; delete through HA
- runtime state (file, position, count, updated) in HA Store keyed by subentry id, versioned with a migrate function
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add, reconfigure and delete through the subentry flow; invalid patterns are form errors
- [x] #2 The preview step shows how many pictures match and the first few
- [x] #3 A rotation steps through files in order, wraps, and continues after a file is removed
- [x] #4 State survives a reload; deleting the subentry drops its state
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
rotations.py keeps state (file, position, count, pattern, updated) in a versioned Store keyed by subentry id; state of deleted rotations is dropped at setup. Adding or deleting a subentry does not reload the entry by itself, and OptionsFlowWithReload refuses update listeners, so the options flow is a plain OptionsFlow and one update listener reloads the entry on any change (options or rotations), as core integrations with subentries do. The subentry flow validates patterns, shows a preview step (count, pattern used, first five) and reuses both steps for reconfigure.
<!-- SECTION:NOTES:END -->
