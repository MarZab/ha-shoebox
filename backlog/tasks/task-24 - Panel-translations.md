---
id: TASK-24
title: 'Panel: translations'
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - panel
milestone: m-4
dependencies:
  - TASK-23
priority: medium
type: task
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every visible string comes from i18n.js and follows the user language with English as fallback. Wording follows HA style: sentence case, HA terms.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No visible text outside the string table
- [ ] #2 Changing the user language changes the panel
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
