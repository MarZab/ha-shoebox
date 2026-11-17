---
id: TASK-5
title: Manifest and brand
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T15:14:00Z'
labels:
  - integration
  - release
milestone: m-0
dependencies:
  - TASK-2
  - TASK-3
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The integration passes hassfest and hacs/action as a standalone repository and looks finished in HA.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 manifest.json: domain and name first, then alphabetical; documentation, issue_tracker, codeowners and version set
- [x] #2 The pillow-heif requirement is a version HA can install
- [x] #3 brand/icon.png and icon@2x.png present; sidebar icon chosen
- [x] #4 hassfest and hacs/action pass in CI
- [x] #5 hassfest passes locally (mise run hassfest)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ci and validate (hassfest, hacs/action) pass on 2230fde.
<!-- SECTION:NOTES:END -->
