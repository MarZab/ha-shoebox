---
id: TASK-16
title: Rotations as config subentries
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 Add, reconfigure and delete through the subentry flow; invalid patterns are form errors
- [ ] #2 The preview step shows how many pictures match and the first few
- [ ] #3 A rotation steps through files in order, wraps, and continues after a file is removed
- [ ] #4 State survives a reload; deleting the subentry drops its state
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
