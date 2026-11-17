---
id: TASK-14
title: 'Spike: media folders other than local'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-2
dependencies: []
priority: low
type: spike
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
HA allows several media_dirs. Decide whether Shoebox works on all of them (paths become "<dir>/<path>") or on the local media folder only.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Outcome in docs/architecture.md; follow-up task if needed
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
