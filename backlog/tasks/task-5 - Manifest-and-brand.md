---
id: TASK-5
title: Manifest and brand
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 manifest.json: domain and name first, then alphabetical; documentation, issue_tracker, codeowners and version set
- [ ] #2 The pillow-heif requirement is a version HA can install
- [ ] #3 brand/icon.png and icon@2x.png present; sidebar icon chosen
- [ ] #4 The Docker HA lists Shoebox Media Manager and opens the Shoebox panel
- [ ] #5 hassfest and hacs/action pass in CI
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
