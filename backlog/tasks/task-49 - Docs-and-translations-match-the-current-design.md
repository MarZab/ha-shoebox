---
id: TASK-49
title: Docs and translations match the current design
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - docs
milestone: m-5
dependencies: []
priority: high
type: docs
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review: services.yaml examples and field descriptions use prefixed paths; move's "to" is described correctly; the rotation step text mentions shuffle; use-cases.md describes the current editor; the README/panel screenshot is retaken; architecture.md lists the current state fields and views; displays.md says the image entity token rotates; security.md says what the media view shows non-admins; README explains adding a custom HACS repository for the first release; smaller stale wording listed in the review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No example or description uses unprefixed paths or describes removed behaviour
- [ ] #2 The README and panel screenshots show the current panel
- [ ] #3 displays.md and security.md are accurate about tokens and what non-admins can see
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
