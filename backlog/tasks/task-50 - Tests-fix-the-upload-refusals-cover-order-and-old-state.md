---
id: TASK-50
title: 'Tests: fix the upload refusals, cover order and old state'
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - tests
milestone: m-5
dependencies: []
priority: medium
type: task
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review: the upload type and missing-file refusal tests never reach those checks (folder ""). Add, within the testing policy: a rotation's order reaches Next (path vs shuffle via the button), and stored state with old fields still loads. Make the file-system error test independent of running as root.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Upload type and missing-part refusals are actually exercised
- [ ] #2 Order through the Next button and old stored state are tested
- [ ] #3 Tests pass as root and as a normal user
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
