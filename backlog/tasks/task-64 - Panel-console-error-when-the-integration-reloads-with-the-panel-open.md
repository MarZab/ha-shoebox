---
id: TASK-64
title: 'Panel: console error when the integration reloads with the panel open'
status: To Do
assignee: []
created_date: '2026-11-17T16:06:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: low
type: bug
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reloading the entry (options or rotation changes) while the Shoebox panel is open logs 'Cannot read properties of undefined (reading module_url)' in the browser: unload removes the sidebar panel and setup registers it again, and Home Assistant's frontend looks it up in between. Present before the single-folder change. Consider keeping the panel registered across a reload when Show in sidebar stays on (removing it only when turned off or on removal).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Reloading the entry with the panel open logs no page error
- [ ] #2 Turning Show in sidebar off still removes the panel; removing the integration removes it
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
