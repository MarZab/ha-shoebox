---
id: TASK-3
title: CI workflows
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - tooling
  - release
milestone: m-0
dependencies:
  - TASK-1
priority: high
type: chore
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub Actions:
- ci.yaml: the same checks as `mise run check`, with coverage, on push and pull request
- validate.yaml: hassfest and hacs/action (category integration), on push, pull request and nightly
- release.yaml: on a tag vX.Y.Z or vX.Y.Z(a|b|rc)N, check it matches manifest.json and create the GitHub release (pre-release for a/b/rc)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ci.yaml and `mise run check` run the same checks
- [ ] #2 validate.yaml runs hassfest and hacs/action
- [ ] #3 release.yaml refuses a tag that does not match manifest.json
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
